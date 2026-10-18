from django.db import models

class UserAddressModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="addresses",)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20)

    address = models.CharField(max_length=200)

    is_default = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"