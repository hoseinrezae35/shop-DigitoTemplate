from django.db import models
from django.core.cache import cache

class AboutPage(models.Model):
    """
    اطلاعات اصلی صفحه درباره ما
    فقط یک رکورد از این مدل مجاز است.
    """

    singleton_key = models.PositiveSmallIntegerField(
        default=1,
        unique=True,
        editable=False
    )

    # اطلاعات اصلی
    brand_name = models.CharField(
        max_length=150,
        default="حسین",
        verbose_name="نام فروشگاه"
    )

    hero_image = models.ImageField(
        upload_to="abouts/hero/",
        blank=True,
        null=True,
        verbose_name="تصویر اصلی"
    )

    hero_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="متن جایگزین تصویر"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال بودن صفحه"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "صفحه درباره ما"
        verbose_name_plural = "صفحه درباره ما"

    def __str__(self):
        return f"صفحه درباره {self.brand_name}"


class AboutParagraph(models.Model):
    """
    پاراگراف های بخش معرفی فروشگاه
    """

    page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="paragraphs",
        verbose_name="صفحه درباره ما"
    )

    title = models.CharField(
        max_length=50,
        verbose_name="عنوان پاراگراف"
    )

    text = models.TextField(
        verbose_name="متن پاراگراف"
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    class Meta:
        verbose_name = "پاراگراف معرفی"
        verbose_name_plural = "پاراگراف های معرفی"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"پاراگراف {self.sort_order} - {self.page.brand_name}"


class AboutFeature(models.Model):
    """
    کارت های ویژگی و مزیت های فروشگاه
    """

    page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="صفحه درباره ما"
    )

    title = models.CharField(
        max_length=150,
        verbose_name="عنوان کارت"
    )

    description = models.TextField(
        verbose_name="توضیحات کارت"
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    class Meta:
        verbose_name = "کارت ویژگی"
        verbose_name_plural = "کارت های ویژگی"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title


class PersonalInformation(models.Model):
    """
    اطلاعات شخصی برای نمایش
    """

    singleton_key = models.PositiveSmallIntegerField(
        default=1,
        unique=True,
        editable=False
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="شماره تماس"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل"
    )

    address = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="آدرس"
    )

    telegram_id = models.CharField(
        max_length=25,
        blank=True,
        verbose_name="ایدی تلگرام"
    )

    whatsapp_id = models.CharField(
        max_length=25,
        blank=True,
        verbose_name="شماره واتساپ"
    )

    instagram_id = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="ایدی اینستاگرام"
    )

    eitaa_id = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="ایدی ایتا"
    )

    footer_paragraph = models.TextField(
        blank=True,
        verbose_name="متن پایین صفحه"
    )

    brand_name = models.CharField(
        max_length=150,
        default="حسین",
        verbose_name="نام فروشگاه"
    )

    brand_image = models.ImageField(
        upload_to="abouts/brand/",
        blank=True,
        null=True,
        verbose_name="تصویر برند"
    )

    brand_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="متن جایگزین تصویر"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال بودن"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete("personal_information_active")

    class Meta:
        verbose_name = "اطلاعات تماس"
        verbose_name_plural = "اطلاعات تماس ها"

    def __str__(self):
        return f"صفحه درباره {self.email}"
