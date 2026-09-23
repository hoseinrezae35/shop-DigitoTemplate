from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Color, Size, Product, ProductImage, ProductComment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    autocomplete_fields = ['parent']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('تصویر و وضعیت', {
            'fields': ('image', 'is_active')
        }),
        ('تاریخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_preview']
    search_fields = ['name']

    def color_preview(self, obj):
        if obj.code:
            return format_html(
                '<div style="width: 30px; height: 30px; background: {}; border: 1px solid #ccc; border-radius: 4px;"></div>',
                obj.code)
        return '-'

    color_preview.short_description = 'پیش‌ نمایش رنگ'


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'پیش‌ نمایش'


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category_display', 'price_display',
        'stock', 'is_available', 'is_featured', 'primary_image_preview', 'is_new', 'is_bestseller'
    ]
    list_filter = [
        'category', 'is_available', 'is_featured', 'is_new', 'is_bestseller',
        'colors', 'sizes', 'created_at'
    ]
    search_fields = ['name', 'sku', 'short_description']
    list_editable = ['is_available', 'is_featured', 'is_new', 'is_bestseller']
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}

    # فیلترهای پیشرفته
    autocomplete_fields = ['category', 'colors', 'sizes']

    inlines = [ProductImageInline]

    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'slug', 'sku', 'category')
        }),
        ('قیمت و موجودی', {
            'fields': ('price', 'discount_price', 'stock', 'is_available')
        }),
        ('توضیحات', {
            'fields': ('short_description', 'description', 'specifications')
        }),
        ('ویژگی‌ها', {
            'fields': ('colors', 'sizes', 'is_featured', 'is_new', 'is_bestseller')
        }),
        ('آمار', {
            'fields': ('views', 'sales'),
            'classes': ('collapse',)
        }),
        ('تاریخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['views', 'sales', 'created_at', 'updated_at']

    def category_display(self, obj):
        if obj.category.parent:
            return format_html('{} → {}', obj.category.parent.name, obj.category.name)
        return obj.category.name

    category_display.short_description = 'دسته‌بندی'

    def price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} تومان</span><br/>'
                '<span style="color: green; font-weight: bold;">{} تومان</span>'
                '<br/><span style="color: red;">{}% تخفیف</span>',
                obj.price, obj.discount_price, obj.discount_percent
            )
        return format_html('<span style="font-weight: bold;">{} تومان</span>', obj.price)

    price_display.short_description = 'قیمت'

    def primary_image_preview(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                primary.image.url)
        first = obj.images.first()
        if first:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                first.image.url)
        return format_html('<span style="color: red;">بدون تصویر</span>')

    primary_image_preview.short_description = 'تصویر'

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

    actions = ['make_available', 'make_unavailable', 'set_featured', 'remove_featured']

    def make_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, 'محصولات منتخب موجود شدند')

    make_available.short_description = 'موجود کردن محصولات انتخاب شده'

    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, 'محصولات منتخب ناموجود شدند')

    make_unavailable.short_description = 'ناموجود کردن محصولات انتخاب شده'

    def set_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, 'محصولات منتخب ویژه شدند')

    set_featured.short_description = 'ویژه کردن محصولات انتخاب شده'

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, 'ویژه بودن محصولات منتخب برداشته شد')

    remove_featured.short_description = 'برداشتن ویژه از محصولات انتخاب شده'


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order']
    list_filter = ['is_primary', 'product__category']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'تصویر'


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "title",
        "recommendation",
        "is_active",
        "created_at",
    )

    list_filter = (
        "recommendation",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "text",
        "user__email",
        "product__name",
    )

    list_editable = (
        "is_active",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 20


from django.contrib import admin

from .models import ProductFavorite


@admin.register(ProductFavorite)
class ProductFavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__email",
        "product__name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )

    list_per_page = 20


admin.site.register(Category, CategoryAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)

admin.site.site_header = 'مدیریت فروشگاه'
admin.site.site_title = 'پنل ادمین'
admin.site.index_title = 'خوش آمدید به پنل مدیریت'
