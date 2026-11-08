from django.http import Http404
from django.views.generic import TemplateView

from .models import AboutPage


class AboutPageView(TemplateView):
    template_name = "abouts/about-me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        about_page, created = AboutPage.objects.get_or_create(
            singleton_key=1
        )

        if not about_page.is_active:
            raise Http404("صفحه درباره ما در دسترس نیست.")

        context["about_page"] = about_page

        context["about_paragraphs"] = (
            about_page.paragraphs
            .filter(is_active=True)
            .order_by("sort_order", "id")
        )

        context["about_features"] = (
            about_page.features
            .filter(is_active=True)
            .order_by("sort_order", "id")
        )

        return context