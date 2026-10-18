from django.contrib import admin

from .models import (Order, OrderItem)
from payment.models import Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ("id", "gateway", "amount", "status", "authority", "ref_id", "created_at")
    readonly_fields = fields
    can_delete = False
    show_change_link = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0

    readonly_fields = (
        "product_name",
        "price",
        "quantity",
        "total_price",
        "created_at",
    )

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "final_price",
        "status",
        "payment_status",
        "tracking_code",
        "created_at",
    )

    list_display_links = (
        "id",
        "user",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__email",
        "user__phone_number",
        "first_name",
        "last_name",
        "phone_number",
        "tracking_code",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "user",
                    "status",
                    "payment_status",
                    "tracking_code",
                )
            }
        ),
        (
            "اطلاعات گیرنده",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "state",
                    "city",
                    "postal_code",
                    "shipping_address",
                )
            }
        ),
        (
            "مبالغ",
            {
                "fields": (
                    "total_price",
                    "shipping_cost",
                    "final_price",
                )
            }
        ),
        (
            "توضیحات",
            {
                "fields": (
                    "description",
                )
            }
        ),
        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )

    inlines = [
        OrderItemInline,
        PaymentInline,
    ]

    ordering = (
        "-created_at",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
        "total_price",
        "created_at",
    )

    search_fields = (
        "product_name",
        "order__id",
    )

    readonly_fields = (
        "created_at",
    )

    list_filter = (
        "created_at",
    )
