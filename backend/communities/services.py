from datetime import timedelta
from decimal import Decimal, ROUND_DOWN, ROUND_UP

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from .models import Bill, Building, FeeType, Installment, Payment, Reminder, Room


def make_number(prefix):
    return f"{prefix}{timezone.now().strftime('%Y%m%d%H%M%S%f')}"


@transaction.atomic
def generate_bills(fee_type_id, period, due_date, room_ids=None):
    fee_type = FeeType.objects.get(pk=fee_type_id, is_active=True)
    rooms = Room.objects.filter(is_active=True)
    if room_ids:
        rooms = rooms.filter(id__in=room_ids)

    created = []
    skipped = 0
    for room in rooms.select_related("building"):
        amount = fee_type.calculate_amount(room)
        bill, was_created = Bill.objects.get_or_create(
            room=room,
            fee_type=fee_type,
            period=period,
            defaults={
                "bill_no": make_number("B"),
                "amount": amount,
                "due_date": due_date,
                "status": Bill.UNPAID,
            },
        )
        if was_created:
            created.append(bill)
        else:
            skipped += 1
    return created, skipped


def _update_bill_status_after_payment(bill):
    if bill.remaining_amount <= Decimal("0.00"):
        bill.status = Bill.PAID
        bill.paid_at = timezone.now()
    elif bill.paid_amount > Decimal("0.00"):
        if bill.status == Bill.UNPAID:
            if bill.due_date < timezone.localdate():
                bill.status = Bill.OVERDUE
            else:
                bill.status = Bill.PARTIAL
    bill.save(update_fields=["status", "paid_at"])


@transaction.atomic
def pay_bill(bill, method, payer="", amount=None):
    if bill.status == Bill.PAID:
        raise ValueError("该账单已缴费")
    if bill.status == Bill.CANCELLED:
        raise ValueError("作废账单不能缴费")
    if bill.has_installments:
        raise ValueError("该账单已分期，请逐期支付")

    pay_amount = Decimal(amount) if amount is not None else bill.amount
    if pay_amount <= Decimal("0.00"):
        raise ValueError("支付金额必须大于 0")
    if pay_amount > bill.remaining_amount:
        raise ValueError(f"支付金额不能超过剩余金额 {bill.remaining_amount}")

    payment = Payment.objects.create(
        payment_no=make_number("P"),
        bill=bill,
        amount=pay_amount,
        method=method,
        payer=payer or bill.room.owner_name,
        receipt_no=make_number("R"),
    )
    _update_bill_status_after_payment(bill)
    return payment


@transaction.atomic
def create_installments(bill, count, first_due_date=None, interval_days=30):
    if bill.status == Bill.PAID:
        raise ValueError("已缴费账单不能分期")
    if bill.status == Bill.CANCELLED:
        raise ValueError("作废账单不能分期")
    if bill.has_installments:
        raise ValueError("该账单已存在分期记录")
    if bill.remaining_amount <= Decimal("0.00"):
        raise ValueError("该账单剩余金额为 0，无需分期")

    total = bill.remaining_amount
    base = (total / count).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    remainder = (total - base * count).quantize(Decimal("0.01"))

    start_date = first_due_date or bill.due_date
    installments = []
    for i in range(count):
        seq = i + 1
        installment_amount = base + (remainder if i == count - 1 else Decimal("0.00"))
        due = start_date + timedelta(days=interval_days * i)
        inst = Installment.objects.create(
            installment_no=make_number("I"),
            bill=bill,
            sequence=seq,
            amount=installment_amount,
            due_date=due,
            status=Installment.UNPAID,
        )
        installments.append(inst)

    if bill.status == Bill.UNPAID:
        if bill.due_date < timezone.localdate():
            bill.status = Bill.OVERDUE
        else:
            bill.status = Bill.PARTIAL
        bill.save(update_fields=["status"])

    return installments


@transaction.atomic
def pay_installment(installment, method, payer=""):
    bill = installment.bill
    if installment.status == Installment.PAID:
        raise ValueError("该分期已缴费")
    if bill.status == Bill.CANCELLED:
        raise ValueError("作废账单不能缴费")

    payment = Payment.objects.create(
        payment_no=make_number("P"),
        bill=bill,
        installment=installment,
        amount=installment.amount,
        method=method,
        payer=payer or bill.room.owner_name,
        receipt_no=make_number("R"),
    )
    installment.status = Installment.PAID
    installment.paid_at = payment.paid_at
    installment.save(update_fields=["status", "paid_at"])

    _update_bill_status_after_payment(bill)
    return payment


@transaction.atomic
def create_overdue_reminders(channel=Reminder.SMS):
    today = timezone.localdate()

    from django.db.models import Exists, OuterRef

    has_installment = Installment.objects.filter(bill=OuterRef("pk"))
    installment_overdue = Installment.objects.filter(
        bill=OuterRef("pk"),
        status__in=[Installment.UNPAID, Installment.OVERDUE],
        due_date__lt=today,
    )
    bills = (
        Bill.objects.filter(status__in=[Bill.UNPAID, Bill.PARTIAL, Bill.OVERDUE])
        .filter(
            models.Q(due_date__lt=today)
            | (models.Q(Exists(has_installment)) & models.Q(Exists(installment_overdue)))
        )
        .select_related("room", "room__building", "fee_type")
        .distinct()
    )

    reminders = []
    for bill in bills:
        bill.status = Bill.OVERDUE
        bill.save(update_fields=["status"])
        Installment.objects.filter(
            bill=bill,
            status__in=[Installment.UNPAID, Installment.OVERDUE],
            due_date__lt=today,
        ).update(status=Installment.OVERDUE)

        if bill.has_installments:
            overdue_insts = list(
                bill.installments.filter(status=Installment.OVERDUE).order_by("sequence").values_list("sequence", flat=True)
            )
            seqs = "、".join(f"第{s}期" for s in overdue_insts) if overdue_insts else ""
            inst_note = f"（{seqs} 已逾期）" if seqs else ""
            message = (
                f"{bill.room.owner_name}您好，您位于{bill.room.building.name}-{bill.room.room_no}的"
                f"{bill.period}{bill.fee_type.name}已申请分期{inst_note}，剩余{bill.remaining_amount}元待缴，请尽快缴纳。"
            )
        else:
            message = (
                f"{bill.room.owner_name}您好，您位于{bill.room.building.name}-{bill.room.room_no}的"
                f"{bill.period}{bill.fee_type.name}欠费{bill.remaining_amount}元，请尽快缴纳。"
            )
        reminders.append(
            Reminder.objects.create(
                reminder_no=make_number("D"),
                bill=bill,
                channel=channel,
                message=message,
            )
        )
    return reminders


def dashboard_stats():
    from django.db.models import Exists, OuterRef

    today = timezone.localdate()

    Bill.objects.filter(
        status__in=[Bill.UNPAID, Bill.PARTIAL], due_date__lt=today
    ).update(status=Bill.OVERDUE)

    has_installment = Installment.objects.filter(bill=OuterRef("pk"))
    inst_overdue = Installment.objects.filter(
        bill=OuterRef("pk"),
        status__in=[Installment.UNPAID, Installment.OVERDUE],
        due_date__lt=today,
    )
    bill_ids = list(
        Bill.objects.filter(status__in=[Bill.UNPAID, Bill.PARTIAL])
        .filter(Exists(has_installment))
        .filter(Exists(inst_overdue))
        .values_list("id", flat=True)
    )
    if bill_ids:
        Bill.objects.filter(id__in=bill_ids).update(status=Bill.OVERDUE)

    Installment.objects.filter(status=Installment.UNPAID, due_date__lt=today).update(status=Installment.OVERDUE)

    bills = Bill.objects.all()
    paid_total = Payment.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    receivable_total = bills.exclude(status=Bill.CANCELLED).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    unpaid_sum = Decimal("0.00")
    for b in bills.filter(status__in=[Bill.UNPAID, Bill.PARTIAL, Bill.OVERDUE]):
        unpaid_sum += b.remaining_amount

    status_counts = dict(bills.values_list("status").annotate(total=Count("id")))
    recent_bills = bills.select_related("room", "room__building", "fee_type")[:8]

    return {
        "building_count": Building.objects.count(),
        "room_count": Room.objects.count(),
        "bill_count": bills.count(),
        "paid_total": paid_total,
        "receivable_total": receivable_total,
        "unpaid_total": unpaid_sum,
        "overdue_count": bills.filter(status=Bill.OVERDUE).count(),
        "status_counts": {
            "unpaid": status_counts.get(Bill.UNPAID, 0),
            "partial": status_counts.get(Bill.PARTIAL, 0),
            "paid": status_counts.get(Bill.PAID, 0),
            "overdue": status_counts.get(Bill.OVERDUE, 0),
            "cancelled": status_counts.get(Bill.CANCELLED, 0),
        },
        "rooms_with_debt": Room.objects.filter(bills__status__in=[Bill.UNPAID, Bill.PARTIAL, Bill.OVERDUE]).distinct().count(),
        "recent_bills": recent_bills,
    }
