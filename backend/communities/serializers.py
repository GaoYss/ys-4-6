from rest_framework import serializers

from .models import Bill, Building, FeeType, Installment, Payment, Reminder, Room


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "building", "building_name", "room_no", "owner_name", "phone", "area", "is_active", "created_at"]


class BuildingSerializer(serializers.ModelSerializer):
    room_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Building
        fields = ["id", "name", "address", "floor_count", "unit_count", "manager", "remark", "room_count", "created_at"]


class BuildingDetailSerializer(BuildingSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta(BuildingSerializer.Meta):
        fields = BuildingSerializer.Meta.fields + ["rooms"]


class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = ["id", "name", "billing_method", "amount", "cycle", "is_active", "description"]


class InstallmentSerializer(serializers.ModelSerializer):
    bill_no = serializers.CharField(source="bill.bill_no", read_only=True)
    room_label = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="bill.room.owner_name", read_only=True)
    fee_name = serializers.CharField(source="bill.fee_type.name", read_only=True)
    period = serializers.CharField(source="bill.period", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Installment
        fields = [
            "id",
            "installment_no",
            "bill",
            "bill_no",
            "room_label",
            "owner_name",
            "fee_name",
            "period",
            "sequence",
            "amount",
            "due_date",
            "status",
            "paid_at",
            "created_at",
            "is_overdue",
        ]
        read_only_fields = ["installment_no", "paid_at", "created_at", "is_overdue"]

    def get_room_label(self, obj):
        return f"{obj.bill.room.building.name}-{obj.bill.room.room_no}"


class BillSerializer(serializers.ModelSerializer):
    room_label = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="room.owner_name", read_only=True)
    phone = serializers.CharField(source="room.phone", read_only=True)
    fee_name = serializers.CharField(source="fee_type.name", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_installments = serializers.BooleanField(read_only=True)
    installment_count = serializers.IntegerField(read_only=True)
    paid_installment_count = serializers.IntegerField(read_only=True)
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = [
            "id",
            "bill_no",
            "room",
            "room_label",
            "owner_name",
            "phone",
            "fee_type",
            "fee_name",
            "period",
            "amount",
            "paid_amount",
            "remaining_amount",
            "status",
            "due_date",
            "generated_at",
            "paid_at",
            "is_overdue",
            "has_installments",
            "installment_count",
            "paid_installment_count",
            "installments",
        ]
        read_only_fields = [
            "bill_no",
            "amount",
            "generated_at",
            "paid_at",
            "is_overdue",
            "paid_amount",
            "remaining_amount",
            "has_installments",
            "installment_count",
            "paid_installment_count",
        ]

    def get_room_label(self, obj):
        return f"{obj.room.building.name}-{obj.room.room_no}"


class PaymentSerializer(serializers.ModelSerializer):
    bill_no = serializers.CharField(source="bill.bill_no", read_only=True)
    room_label = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="bill.room.owner_name", read_only=True)
    fee_name = serializers.CharField(source="bill.fee_type.name", read_only=True)
    period = serializers.CharField(source="bill.period", read_only=True)
    installment_no = serializers.CharField(source="installment.installment_no", read_only=True, allow_null=True)
    installment_sequence = serializers.IntegerField(source="installment.sequence", read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_no",
            "bill",
            "bill_no",
            "installment",
            "installment_no",
            "installment_sequence",
            "room_label",
            "owner_name",
            "fee_name",
            "period",
            "amount",
            "method",
            "paid_at",
            "payer",
            "receipt_no",
        ]
        read_only_fields = ["payment_no", "receipt_no", "paid_at", "installment_no", "installment_sequence"]

    def get_room_label(self, obj):
        return f"{obj.bill.room.building.name}-{obj.bill.room.room_no}"


class ReminderSerializer(serializers.ModelSerializer):
    bill_no = serializers.CharField(source="bill.bill_no", read_only=True)
    room_label = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="bill.room.owner_name", read_only=True)
    phone = serializers.CharField(source="bill.room.phone", read_only=True)
    amount = serializers.DecimalField(source="bill.amount", max_digits=10, decimal_places=2, read_only=True)
    due_date = serializers.DateField(source="bill.due_date", read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "reminder_no",
            "bill",
            "bill_no",
            "room_label",
            "owner_name",
            "phone",
            "amount",
            "due_date",
            "channel",
            "message",
            "status",
            "sent_at",
        ]
        read_only_fields = ["reminder_no", "sent_at"]

    def get_room_label(self, obj):
        return f"{obj.bill.room.building.name}-{obj.bill.room.room_no}"


class CreateInstallmentsSerializer(serializers.Serializer):
    count = serializers.IntegerField(min_value=2, max_value=12)
    first_due_date = serializers.DateField(required=False)
    interval_days = serializers.IntegerField(min_value=1, max_value=365, default=30, required=False)
