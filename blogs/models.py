from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(
        max_length=120,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته‌بندی والد",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "دسته‌بندی مقاله"
        verbose_name_plural = "دسته‌بندی‌های مقالات"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")
    slug = models.SlugField(
        max_length=60,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشرشده"
        ARCHIVED = "archived", "بایگانی‌شده"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="blog_posts",
        verbose_name="کاربر",
    )
    author = models.CharField(max_length=25, verbose_name='نویسنده')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="دسته‌بندی",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="برچسب‌ها",
    )

    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(
        max_length=220,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="خلاصه مقاله",
    )
    content = models.TextField(verbose_name="متن مقاله")

    featured_image = models.ImageField(
        upload_to="blog/covers/",
        blank=True,
        null=True,
        verbose_name="تصویر شاخص",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="وضعیت انتشار",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="مقاله ویژه",
    )

    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="عنوان سئو",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="توضیحات سئو",
    )

    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    reading_time = models.PositiveSmallIntegerField(
        default=2,
        verbose_name="زمان مطالعه (دقیقه)"
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ انتشار",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return (
                self.status == self.Status.PUBLISHED
                and self.published_at is not None
                and self.published_at <= timezone.now()
        )
