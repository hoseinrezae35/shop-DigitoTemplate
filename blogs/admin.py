from django.contrib import admin
from django.utils import timezone

from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("parent",)
    list_per_page = 25


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 25


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "author",
        "category",
        "status",
        "is_featured",
        "views",
        "published_at",
    )
    list_filter = (
        "status",
        "is_featured",
        "category",
        "published_at",
        "created_at",
    )
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "author",
        "user__username",
        "user__email",
    )
    list_editable = ("status", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("user", "category", "tags")
    filter_horizontal = ("tags",)
    readonly_fields = (
        "views",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "published_at"
    list_per_page = 20

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "title",
                "slug",
                "user",
                "author",
                "category",
                "tags",
            )
        }),
        ("محتوای مقاله", {
            "fields": (
                "excerpt",
                "content",
                "featured_image",
            )
        }),
        ("انتشار", {
            "fields": (
                "status",
                "is_featured",
                "published_at",
            )
        }),
        ("سئو", {
            "fields": (
                "meta_title",
                "meta_description",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "views",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="وضعیت انتشار")
    def publication_status(self, obj):
        if obj.status == Post.Status.PUBLISHED and (
                obj.published_at and obj.published_at <= timezone.now()
        ):
            return "منتشرشده"
        if obj.status == Post.Status.DRAFT:
            return "پیش‌نویس"
        if obj.status == Post.Status.ARCHIVED:
            return "بایگانی‌شده"
        return "در انتظار انتشار"
