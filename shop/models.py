from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, verbose_name="اسلاگ")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def get_descendant_ids(self):
        all_categories = Category.objects.values('id', 'parent_id')

        children_map = {}
        for cat in all_categories:
            children_map.setdefault(cat['parent_id'], []).append(cat['id'])

        result = [self.id]
        stack = [self.id]
        while stack:
            current_id = stack.pop()
            children_ids = children_map.get(current_id, [])
            result.extend(children_ids)
            stack.extend(children_ids)

        return result

    @classmethod
    def search_category_ids(cls, keyword):

        ids = []

        for category in cls.objects.filter(name__icontains=keyword):
            ids.extend(category.get_descendant_ids())

        return list(set(ids))

    def get_ancestors(self, include_self=True):
        """
        لیست دسته‌ها رو از ریشه (بالاترین سطح) تا خود دسته برمی‌گردونه
        """
        ancestors = []
        node = self if include_self else self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        return list(reversed(ancestors))

    @classmethod
    def get_menu_tree(cls):
        """
        کل دسته‌بندی‌های فعال رو با یک کوئری می‌خونه
        و به صورت درخت (nested) برمی‌گردونه.
        """
        categories = list(
            cls.objects.filter(is_active=True).only('id', 'name', 'slug', 'parent_id')
        )

        children_map = {}
        for cat in categories:
            children_map.setdefault(cat.parent_id, []).append(cat)

        def attach_children(cat):
            cat.children_list = children_map.get(cat.id, [])
            for child in cat.children_list:
                attach_children(child)
            return cat

        roots = children_map.get(None, [])
        return [attach_children(root) for root in roots]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category-detail', args=[self.id])

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    price = models.DecimalField(max_digits=12, decimal_places=0)
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=0,
        blank=True, null=True
    )

    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    short_description = models.TextField(max_length=250)
    description = models.TextField(max_length=250)
    specifications = models.JSONField(default=dict, blank=True)

    colors = models.ManyToManyField(Color, related_name='products', blank=True)
    sizes = models.ManyToManyField(Size, related_name='products', blank=True)
    is_featured = models.BooleanField(default=False, verbose_name="محصول ویژه")
    is_new = models.BooleanField(default=False, verbose_name="محصول جدید")
    is_bestseller = models.BooleanField(default=False, verbose_name="پرفروش")

    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    sales = models.PositiveIntegerField(default=0, verbose_name="تعداد فروش")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[self.id])

    @property
    def none_stock(self):
        if self.stock <= 0:
            return False
        return True

    @property
    def final_price(self):
        if self.discount_price and self.discount_price > 0:
            return self.discount_price
        return self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.discount_price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def primary_image(self):

        try:
            primary_qs = self.images.filter(is_primary=True)
            if primary_qs.exists():
                return primary_qs.first().image.url
            first_qs = self.images.first()
            if first_qs:
                return first_qs.image.url
        except:
            pass
        return '/static/image/no-image.png'

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-is_primary']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(id=self.id).update(
                is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"تصویر {self.product.name if self.product_id else self.id}"


class ProductComment(models.Model):
    class Recommendation(models.TextChoices):
        RECOMMENDED = "recommended", "پیشنهاد می‌شود"
        NOT_RECOMMENDED = "not_recommended", "پیشنهاد نمی‌شود"

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="محصول"
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="product_comments",
        verbose_name="کاربر"
    )

    title = models.CharField(
        max_length=200,
        default='درباره ی محصول',
        verbose_name="عنوان دیدگاه"
    )

    text = models.TextField(
        verbose_name="متن دیدگاه"
    )

    recommendation = models.CharField(
        max_length=20,
        choices=Recommendation.choices,
        default=Recommendation.RECOMMENDED.value,
        verbose_name="پیشنهاد"
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="وضعیت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class ProductFavorite(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="favorite_products",
        verbose_name="کاربر"
    )

    product = models.ForeignKey(
        "shop.Product",
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="محصول"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن"
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name}"
