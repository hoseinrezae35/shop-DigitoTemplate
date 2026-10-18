from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "phone", "message")
    list_editable = ("status",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        ("اطلاعات فرستنده", {
            "fields": ("name", "phone"),
        }),
        ("محتوای پیام", {
            "fields": ("message",),
        }),
        ("پیگیری پیام", {
            "fields": ("status", "created_at"),
        }),
    )
