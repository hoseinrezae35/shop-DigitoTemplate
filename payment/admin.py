from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Payment, PaymentGateway
from order.models import PaymentStatus


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # ---------- نمایش لیست ----------
    list_display = (
        "short_id",
        "order_link",
        "gateway_badge",
        "amount_display",
        "status_badge",
        "authority_short",
        "ref_id",
        "created_at",
        "paid_at",
    )

    list_display_links = ("short_id", "order_link")

    list_filter = (
        "status",
        "gateway",
        ("created_at", admin.DateFieldListFilter),
        ("paid_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "=authority",
        "=ref_id",
        "order__id",
        "order__user__phone",   # در صورت وجود
        "order__user__email",   # در صورت وجود
        "error_code",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    list_per_page = 50

    list_select_related = ("order",)

    # ---------- فرم جزئیات ----------
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "paid_at",
        "status_badge_large",
        "gateway_badge_large",
    )

    fieldsets = (
        ("اطلاعات پایه", {
            "fields": (
                "id",
                "order",
                "gateway_badge_large",
                "amount",
                "status_badge_large",
            )
        }),
        ("اطلاعات درگاه", {
            "fields": (
                "authority",
                "ref_id",
            )
        }),
        ("خطاها", {
            "classes": ("collapse",),
            "fields": (
                "error_code",
                "error_message",
            )
        }),
        ("تاریخ‌ها", {
            "fields": (
                "created_at",
                "paid_at",
                "updated_at",
            )
        }),
    )

    # ---------- اکشن‌ها ----------
    actions = ("mark_as_paid", "mark_as_failed", "mark_as_refunded")

    # ---------- بهینه‌سازی کوئری ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("order")

    # ---------- ستون‌های سفارشی ----------
    @admin.display(description="شناسه", ordering="id")
    def short_id(self, obj):
        return str(obj.id)[:8] + "…"

    @admin.display(description="سفارش")
    def order_link(self, obj):
        if not obj.order_id:
            return "-"
        url = reverse("admin:order_order_change", args=[obj.order_id])
        return format_html('<a href="{}">#{}</a>', url, obj.order_id)

    @admin.display(description="درگاه", ordering="gateway")
    def gateway_badge(self, obj):
        colors = {
            PaymentGateway.ZARINPAL: "#ffcc00",
        }
        color = colors.get(obj.gateway, "#888")
        return format_html(
            '<span style="background:{};color:#000;padding:2px 8px;'
            'border-radius:6px;font-size:11px;">{}</span>',
            color,
            obj.get_gateway_display(),
        )

    @admin.display(description="مبلغ (ریال)", ordering="amount")
    def amount_display(self, obj):
        return f"{obj.amount:,}"

    @admin.display(description="وضعیت", ordering="status")
    def status_badge(self, obj):
        return self._status_badge(obj.status, small=True)

    @admin.display(description="وضعیت")
    def status_badge_large(self, obj):
        return self._status_badge(obj.status, small=False)

    @admin.display(description="درگاه")
    def gateway_badge_large(self, obj):
        return self.gateway_badge(obj)

    @admin.display(description="Authority")
    def authority_short(self, obj):
        if not obj.authority:
            return "-"
        return obj.authority[:12] + "…" if len(obj.authority) > 12 else obj.authority

    # ---------- هلپر ----------
    @staticmethod
    def _status_badge(status, small=True):
        mapping = {
            PaymentStatus.PENDING:  ("#f0ad4e", "در انتظار"),
            PaymentStatus.SUCCESS:  ("#28a745", "موفق"),
            PaymentStatus.FAILED:   ("#dc3545", "ناموفق"),
            PaymentStatus.REFUNDED: ("#6c757d", "برگردانده شده"),
        }
        color, label = mapping.get(status, ("#888", status))
        padding = "2px 8px" if small else "6px 14px"
        font = "11px" if small else "13px"
        return format_html(
            '<span style="background:{};color:#fff;padding:{};'
            'border-radius:6px;font-size:{};">{}</span>',
            color, padding, font, label,
        )

    # ---------- اکشن‌ها ----------
    @admin.action(description="علامت‌گذاری به عنوان پرداخت موفق")
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status=PaymentStatus.PENDING).update(
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
        )
        self.message_user(request, f"{updated} پرداخت به عنوان موفق علامت زده شد.")

    @admin.action(description="علامت‌گذاری به عنوان ناموفق")
    def mark_as_failed(self, request, queryset):
        updated = queryset.exclude(status=PaymentStatus.SUCCESS).update(
            status=PaymentStatus.FAILED,
        )
        self.message_user(request, f"{updated} پرداخت به عنوان ناموفق علامت زده شد.")

    @admin.action(description="علامت‌گذاری به عنوان لغو شده")
    def mark_as_refunded(self, request, queryset):
        updated = queryset.filter(status=PaymentStatus.PENDING).update(
            status=PaymentStatus.FAILED,
        )
        self.message_user(request, f"{updated} پرداخت برگردانده شده.")

    # ---------- غیرفعال کردن افزودن/ویرایش دستی ----------
    def has_add_permission(self, request):
        # پرداخت‌ها باید توسط سیستم ساخته شوند نه دستی
        return False

    def has_change_permission(self, request, obj=None):
        # اجازه ویرایش فقط برای سوپرکاربر (برای رفع مشکل)
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # پرداخت‌ها نباید حذف شوند
        return False