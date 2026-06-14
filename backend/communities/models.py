from decimal import Decimal

from django.db import models
from django.utils import timezone


class Building(models.Model):
    name = models.CharField("楼栋名称", max_length=80, unique=True)
    address = models.CharField("地址", max_length=200, blank=True)
    floor_count = models.PositiveIntegerField("楼层数", default=1)
    unit_count = models.PositiveIntegerField("单元数", default=1)
    manager = models.CharField("楼管员", max_length=50, blank=True)
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "楼栋"
        verbose_name_plural = "楼栋"

    def __str__(self):
        return self.name


class Room(models.Model):
    building = models.ForeignKey(Building, related_name="rooms", on_delete=models.CASCADE)
    room_no = models.CharField("房号", max_length=40)
    owner_name = models.CharField("业主姓名", max_length=50)
    phone = models.CharField("联系电话", max_length=30, blank=True)
    area = models.DecimalField("建筑面积", max_digits=8, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField("是否入住", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["building__name", "room_no"]
        unique_together = ("building", "room_no")
        verbose_name = "房屋"
        verbose_name_plural = "房屋"

    def __str__(self):
        return f"{self.building.name}-{self.room_no}"


class FeeType(models.Model):
    FIXED = "fixed"
    AREA = "area"
    BILLING_METHOD_CHOICES = (
        (FIXED, "固定金额"),
        (AREA, "按面积"),
    )
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CYCLE_CHOICES = (
        (MONTHLY, "月度"),
        (QUARTERLY, "季度"),
        (YEARLY, "年度"),
    )

    name = models.CharField("费用名称", max_length=80, unique=True)
    billing_method = models.CharField("计费方式", max_length=20, choices=BILLING_METHOD_CHOICES, default=FIXED)
    amount = models.DecimalField("金额或单价", max_digits=10, decimal_places=2)
    cycle = models.CharField("计费周期", max_length=20, choices=CYCLE_CHOICES, default=MONTHLY)
    is_active = models.BooleanField("启用", default=True)
    description = models.TextField("说明", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "费用类型"
        verbose_name_plural = "费用类型"

    def __str__(self):
        return self.name

    def calculate_amount(self, room):
        if self.billing_method == self.AREA:
            return (self.amount * room.area).quantize(Decimal("0.01"))
        return self.amount


class Bill(models.Model):
    UNPAID = "unpaid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (UNPAID, "待缴费"),
        (PAID, "已缴费"),
        (OVERDUE, "已逾期"),
        (CANCELLED, "已作废"),
    )

    bill_no = models.CharField("账单编号", max_length=40, unique=True)
    room = models.ForeignKey(Room, related_name="bills", on_delete=models.PROTECT)
    fee_type = models.ForeignKey(FeeType, related_name="bills", on_delete=models.PROTECT)
    period = models.CharField("账期", max_length=20)
    amount = models.DecimalField("应收金额", max_digits=10, decimal_places=2)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default=UNPAID)
    due_date = models.DateField("截止日期")
    generated_at = models.DateTimeField("生成时间", auto_now_add=True)
    paid_at = models.DateTimeField("缴费时间", null=True, blank=True)

    class Meta:
        ordering = ["-generated_at"]
        unique_together = ("room", "fee_type", "period")
        verbose_name = "费用账单"
        verbose_name_plural = "费用账单"

    def __str__(self):
        return self.bill_no

    @property
    def is_overdue(self):
        return self.status in {self.UNPAID, self.OVERDUE} and self.due_date < timezone.localdate()


class Payment(models.Model):
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK = "bank"
    CASH = "cash"
    METHOD_CHOICES = (
        (WECHAT, "微信"),
        (ALIPAY, "支付宝"),
        (BANK, "银行卡"),
        (CASH, "现金"),
    )

    payment_no = models.CharField("支付流水号", max_length=40, unique=True)
    bill = models.OneToOneField(Bill, related_name="payment", on_delete=models.PROTECT)
    amount = models.DecimalField("实收金额", max_digits=10, decimal_places=2)
    method = models.CharField("支付方式", max_length=20, choices=METHOD_CHOICES, default=WECHAT)
    paid_at = models.DateTimeField("支付时间", default=timezone.now)
    payer = models.CharField("付款人", max_length=50, blank=True)
    receipt_no = models.CharField("票据编号", max_length=40, unique=True)

    class Meta:
        ordering = ["-paid_at"]
        verbose_name = "缴费记录"
        verbose_name_plural = "缴费记录"

    def __str__(self):
        return self.payment_no


class Reminder(models.Model):
    SMS = "sms"
    PHONE = "phone"
    WECHAT = "wechat"
    NOTICE = "notice"
    CHANNEL_CHOICES = (
        (SMS, "短信"),
        (PHONE, "电话"),
        (WECHAT, "微信"),
        (NOTICE, "纸质通知"),
    )
    PENDING = "pending"
    SENT = "sent"
    STATUS_CHOICES = (
        (PENDING, "待发送"),
        (SENT, "已发送"),
    )

    reminder_no = models.CharField("催缴编号", max_length=40, unique=True)
    bill = models.ForeignKey(Bill, related_name="reminders", on_delete=models.CASCADE)
    channel = models.CharField("催缴渠道", max_length=20, choices=CHANNEL_CHOICES, default=SMS)
    message = models.TextField("催缴内容")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default=SENT)
    sent_at = models.DateTimeField("发送时间", default=timezone.now)

    class Meta:
        ordering = ["-sent_at"]
        verbose_name = "欠费催缴"
        verbose_name_plural = "欠费催缴"

    def __str__(self):
        return self.reminder_no
