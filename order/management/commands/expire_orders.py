from django.core.management.base import BaseCommand
from django.utils import timezone

from order.models import Order, OrderStatus


class Command(BaseCommand):
    help = "لغو سفارش‌های پرداخت‌نشده و آزاد کردن موجودی رزروشده"

    def handle(self, *args, **options):

        now = timezone.now()

        orders = (
            Order.objects
            .filter(
                status=OrderStatus.PENDING,
                payment_expires_at__isnull=False,
                payment_expires_at__lte=now,
            )
            .only("id")
        )

        expired_count = 0

        for order in orders:

            released = order.release_reserved_stock()

            if released:
                expired_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"سفارش #{order.id} منقضی و موجودی آن آزاد شد."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{expired_count} سفارش منقضی پردازش شد."
            )
        )