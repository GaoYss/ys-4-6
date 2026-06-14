from django.contrib import admin

from .models import Bill, Building, FeeType, Payment, Reminder, Room


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "floor_count", "unit_count", "created_at")
    search_fields = ("name", "address")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_no", "building", "owner_name", "phone", "area", "is_active")
    list_filter = ("building", "is_active")
    search_fields = ("room_no", "owner_name", "phone")


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "billing_method", "amount", "cycle", "is_active")
    list_filter = ("billing_method", "cycle", "is_active")


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("bill_no", "room", "fee_type", "period", "amount", "status", "due_date")
    list_filter = ("status", "fee_type", "period")
    search_fields = ("bill_no", "room__room_no", "room__owner_name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_no", "bill", "amount", "method", "paid_at", "receipt_no")
    list_filter = ("method", "paid_at")
    search_fields = ("payment_no", "receipt_no", "bill__bill_no")


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("reminder_no", "bill", "channel", "status", "sent_at")
    list_filter = ("channel", "status")
    search_fields = ("reminder_no", "bill__bill_no", "bill__room__owner_name")
