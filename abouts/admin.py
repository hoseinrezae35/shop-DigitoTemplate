from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AboutPage,
    AboutParagraph,
    AboutFeature,
    PersonalInformation
)


class AboutParagraphInline(admin.StackedInline):
    model = AboutParagraph

    extra = 1

    fields = (
        "title",
        "text",
        "sort_order",
        "is_active",
    )

    ordering = ("sort_order",)


class AboutFeatureInline(admin.StackedInline):
    model = AboutFeature

    extra = 1

    fields = (
        "title",
        "description",
        "sort_order",
        "is_active",
    )

    ordering = ("sort_order",)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "is_active",
        "updated_at",
    )

    list_display_links = (
        "brand_name",
    )

    readonly_fields = (
        "singleton_key",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی فروشگاه",
            {
                "fields": (
                    "brand_name",
                    "is_active",
                )
            },
        ),

        (
            "تصویر صفحه درباره ما",
            {
                "fields": (
                    "hero_image",
                    "hero_image_alt",
                )
            },
        ),

        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "singleton_key",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [
        AboutParagraphInline,
        AboutFeatureInline,
    ]

    save_on_top = True

    def has_add_permission(self, request):
        if AboutPage.objects.exists():
            return False

        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PersonalInformation)
class PersonalInformationAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "email",
        "phone_number",
        "is_active",
        "updated_at",
        "brand_image_preview",
    )

    list_display_links = ("brand_name",)

    search_fields = (
        "brand_name",
        "email",
        "phone_number",
    )

    list_filter = (
        "is_active",
        "updated_at",
    )

    readonly_fields = (
        "singleton_key",
        "updated_at",
        "brand_image_preview",
    )

    fieldsets = (
        ("اطلاعات فروشگاه", {
            "fields": (
                "brand_name",
                "brand_image",
                "brand_image_alt",
                "footer_paragraph",
            )
        }),

        ("اطلاعات تماس", {
            "fields": (
                "phone_number",
                "email",
                "address",
            )
        }),

        ("شبکه‌های اجتماعی", {
            "fields": (
                "telegram_id",
                "whatsapp_id",
                "instagram_id",
                "eitaa_id",
            )
        }),

        ("تنظیمات", {
            "fields": (
                "is_active",
                "singleton_key",
                "updated_at",
            )
        }),
    )

    def brand_image_preview(self, obj):
        if obj and obj.brand_image:
            return format_html(
                '<img src="{}" width="100" height="70" '
                'style="object-fit: contain; border-radius: 8px;" />',
                obj.brand_image.url
            )

        return "تصویری ثبت نشده است"

    brand_image_preview.short_description = "پیش‌نمایش تصویر برند"

    def has_add_permission(self, request):
        return not PersonalInformation.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
