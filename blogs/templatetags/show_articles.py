
from django import template
from django.utils import timezone

from blogs.models import Post

register = template.Library()


@register.inclusion_tag("include/home-articles.html")
def show_articles_home():
    articles = (
        Post.objects
        .filter(
            status=Post.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        )
        .select_related("user", "category")
        .order_by("-published_at")[:10]
    )

    return {
        "articles": articles,
    }
