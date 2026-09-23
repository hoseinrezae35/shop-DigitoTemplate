from django.views.generic import TemplateView


class ContactUsView(TemplateView):
    template_name = 'contactus/contact.html'
