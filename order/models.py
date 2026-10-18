from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction
from accounts.models import User
from dashboard.models import UserAddressModel
from shop.models import Product


class OrderStatus(models.TextChoices):
    PENDING = "pending", "در انتظار پرداخت"
    PAID = "paid", "پرداخت شده"
    PROCESSING = "processing", "در حال پردازش"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل داده شده"
    CANCELED = "canceled", "لغو شده"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "در انتظار پرداخت"
    SUCCESS = "success", "پرداخت موفق"
    FAILED = "failed", "پرداخت ناموفق"
    REFUNDED = "refunded", "مبلغ بازگردانده شده"


class ShippingMethod(models.TextChoices):
    TIPAX = "tipax", "ارسال با تیپاکس"
    PICKUP = "pickup", "دریافت حضوری"


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    address = models.ForeignKey(
        UserAddressModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    # Snapshot اطلاعات گیرنده
    first_name = models.CharField(
        max_length=50,
        verbose_name="نام گیرنده"
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name="نام خانوادگی گیرنده"
    )

    phone_number = models.CharField(
        max_length=20,
        verbose_name="شماره تماس"
    )

    state = models.CharField(
        max_length=50,
        verbose_name="استان"
    )

    city = models.CharField(
        max_length=50,
        verbose_name="شهر"
    )

    postal_code = models.CharField(
        max_length=20,
        verbose_name="کد پستی",
        blank=True,
        null=True,
    )

    shipping_address = models.CharField(
        max_length=300,
        verbose_name="آدرس ارسال"
    )

    shipping_method = models.CharField(
        max_length=20,
        choices=ShippingMethod.choices,
        default=ShippingMethod.TIPAX,
        verbose_name="روش دریافت"
    )
    # مبالغ سفارش
    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ کالاها"
    )

    shipping_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه ارسال"
    )

    final_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ نهایی"
    )

    tax_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مالیات"
    )

    tax_percent = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="درصد مالیات"
    )

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING,
                              db_index=True,
                              verbose_name="وضعیت سفارش"
                              )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت پرداخت"
    )

    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="کد پیگیری"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    payment_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ انقضای پرداخت"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"سفارش #{self.pk} - {self.user}"

    def calculate_tax(self):
        return int(self.total_price * self.tax_percent / 100)

    def calculate_final_price(self):
        tax = self.calculate_tax()

        return (
                self.total_price
                + tax
                + self.shipping_cost
        )

    def release_reserved_stock(self):
        if self.status != OrderStatus.PENDING:
            return False

        with transaction.atomic():
            order = (
                Order.objects
                .select_for_update()
                .prefetch_related("items__product")
                .get(pk=self.pk)
            )

            if order.status != OrderStatus.PENDING:
                return False

            for item in order.items.all():
                product = (
                    Product.objects
                    .select_for_update()
                    .get(pk=item.product_id)
                )

                product.stock += item.quantity

                product.save(
                    update_fields=[
                        "stock",
                        "updated_at",
                    ]
                )

            order.status = OrderStatus.CANCELED
            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return True


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="محصول"
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name="نام محصول"
    )

    price = models.PositiveBigIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="قیمت واحد"
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="تعداد"
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="قیمت کل"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def calculate_total_price(self):
        return self.price * self.quantity
