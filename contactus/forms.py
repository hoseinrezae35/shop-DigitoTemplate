from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "message"]

        labels = {
            "name": "نام و نام خانوادگی",
            "phone": "شماره تلفن",
            "message": "متن پیام",
        }

        error_messages = {
            "name": {
                "required": "لطفاً نام و نام خانوادگی خود را وارد کنید.",
            },
            "phone": {
                "required": "لطفاً شماره تلفن خود را وارد کنید.",
            },
            "message": {
                "required": "لطفاً متن پیام خود را وارد کنید.",
            },
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if len(name) < 3:
            raise forms.ValidationError(
                "نام و نام خانوادگی باید حداقل ۳ کاراکتر باشد."
            )

        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if len(phone) < 10:
            raise forms.ValidationError(
                "شماره تلفن باید حداقل ۱۰ رقم باشد."
            )

        return phone

    def clean_message(self):
        message = self.cleaned_data["message"].strip()

        if len(message) < 5:
            raise forms.ValidationError(
                "متن پیام باید حداقل ۵ کاراکتر باشد."
            )

        return message
