from django.db import models


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        READ = "read", "بررسی‌شده"
        REPLIED = "replied", "پاسخ‌داده‌شده"
        CLOSED = "closed", "بسته‌شده"

    name = models.CharField(
        max_length=100,
        verbose_name="نام و نام خانوادگی",
    )

    phone = models.CharField(max_length=15, verbose_name="تلفن")

    message = models.TextField(
        max_length=5000,
        verbose_name="متن پیام",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="وضعیت",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ارسال",
    )

    # email = models.EmailField( max_length=254, verbose_name="ایمیل",)
    # subject = models.CharField(max_length=200, verbose_name="موضوع پیام")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.phone}"
