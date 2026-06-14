import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Building",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="楼栋名称")),
                ("address", models.CharField(blank=True, max_length=200, verbose_name="地址")),
                ("floor_count", models.PositiveIntegerField(default=1, verbose_name="楼层数")),
                ("unit_count", models.PositiveIntegerField(default=1, verbose_name="单元数")),
                ("manager", models.CharField(blank=True, max_length=50, verbose_name="楼管员")),
                ("remark", models.TextField(blank=True, verbose_name="备注")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
            ],
            options={"verbose_name": "楼栋", "verbose_name_plural": "楼栋", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="FeeType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="费用名称")),
                (
                    "billing_method",
                    models.CharField(
                        choices=[("fixed", "固定金额"), ("area", "按面积")],
                        default="fixed",
                        max_length=20,
                        verbose_name="计费方式",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="金额或单价")),
                (
                    "cycle",
                    models.CharField(
                        choices=[("monthly", "月度"), ("quarterly", "季度"), ("yearly", "年度")],
                        default="monthly",
                        max_length=20,
                        verbose_name="计费周期",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="启用")),
                ("description", models.TextField(blank=True, verbose_name="说明")),
            ],
            options={"verbose_name": "费用类型", "verbose_name_plural": "费用类型", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("room_no", models.CharField(max_length=40, verbose_name="房号")),
                ("owner_name", models.CharField(max_length=50, verbose_name="业主姓名")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="联系电话")),
                ("area", models.DecimalField(decimal_places=2, default="0.00", max_digits=8, verbose_name="建筑面积")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否入住")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                (
                    "building",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rooms", to="communities.building"),
                ),
            ],
            options={"verbose_name": "房屋", "verbose_name_plural": "房屋", "ordering": ["building__name", "room_no"]},
        ),
        migrations.CreateModel(
            name="Bill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bill_no", models.CharField(max_length=40, unique=True, verbose_name="账单编号")),
                ("period", models.CharField(max_length=20, verbose_name="账期")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="应收金额")),
                (
                    "status",
                    models.CharField(
                        choices=[("unpaid", "待缴费"), ("paid", "已缴费"), ("overdue", "已逾期"), ("cancelled", "已作废")],
                        default="unpaid",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                ("due_date", models.DateField(verbose_name="截止日期")),
                ("generated_at", models.DateTimeField(auto_now_add=True, verbose_name="生成时间")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="缴费时间")),
                (
                    "fee_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bills", to="communities.feetype"),
                ),
                (
                    "room",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bills", to="communities.room"),
                ),
            ],
            options={"verbose_name": "费用账单", "verbose_name_plural": "费用账单", "ordering": ["-generated_at"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payment_no", models.CharField(max_length=40, unique=True, verbose_name="支付流水号")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="实收金额")),
                (
                    "method",
                    models.CharField(
                        choices=[("wechat", "微信"), ("alipay", "支付宝"), ("bank", "银行卡"), ("cash", "现金")],
                        default="wechat",
                        max_length=20,
                        verbose_name="支付方式",
                    ),
                ),
                ("paid_at", models.DateTimeField(default=timezone.now, verbose_name="支付时间")),
                ("payer", models.CharField(blank=True, max_length=50, verbose_name="付款人")),
                ("receipt_no", models.CharField(max_length=40, unique=True, verbose_name="票据编号")),
                (
                    "bill",
                    models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="payment", to="communities.bill"),
                ),
            ],
            options={"verbose_name": "缴费记录", "verbose_name_plural": "缴费记录", "ordering": ["-paid_at"]},
        ),
        migrations.CreateModel(
            name="Reminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reminder_no", models.CharField(max_length=40, unique=True, verbose_name="催缴编号")),
                (
                    "channel",
                    models.CharField(
                        choices=[("sms", "短信"), ("phone", "电话"), ("wechat", "微信"), ("notice", "纸质通知")],
                        default="sms",
                        max_length=20,
                        verbose_name="催缴渠道",
                    ),
                ),
                ("message", models.TextField(verbose_name="催缴内容")),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "待发送"), ("sent", "已发送")],
                        default="sent",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                ("sent_at", models.DateTimeField(default=timezone.now, verbose_name="发送时间")),
                (
                    "bill",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reminders", to="communities.bill"),
                ),
            ],
            options={"verbose_name": "欠费催缴", "verbose_name_plural": "欠费催缴", "ordering": ["-sent_at"]},
        ),
        migrations.AlterUniqueTogether(name="room", unique_together={("building", "room_no")}),
        migrations.AlterUniqueTogether(name="bill", unique_together={("room", "fee_type", "period")}),
    ]
