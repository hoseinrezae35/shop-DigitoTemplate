import uuid

from django.db import models

from order.models import Order, PaymentStatus


class PaymentGateway(models.TextChoices):
    ZARINPAL = "zarinpal", "زرین پال"


class Payment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="سفارش",
    )

    gateway = models.CharField(
        max_length=30,
        choices=PaymentGateway.choices,
        default=PaymentGateway.ZARINPAL,
        verbose_name="درگاه پرداخت",
    )

    # مبلغی که دقیقاً به درگاه ارسال شده - ریال
    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ پرداخت - ریال",
    )

    authority = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Authority",
    )

    ref_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شماره پیگیری",
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="کد خطا",
    )

    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name="پیام خطا",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پرداخت",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.pk} - Order #{self.order_id}"