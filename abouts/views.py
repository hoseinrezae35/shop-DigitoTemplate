from django.views.generic import TemplateView


class AboutMeView(TemplateView):
    template_name = 'abouts/about-me.html'
