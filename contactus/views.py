from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import ContactForm


class ContactUsView(FormView):
    template_name = "contactus/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contactus:contact")

    def form_valid(self, form):
        form.save()

        messages.success(
            self.request,
            "پیام شما با موفقیت ارسال شد. "
            "در اولین فرصت با شما تماس می‌گیریم."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
