from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import Post


class BlogListView(ListView):
    model = Post
    template_name = "blogs/list-blog.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                status=Post.Status.PUBLISHED,
                published_at__isnull=False,
                published_at__lte=timezone.now(),
            )
            .select_related("user", "category")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["featured_articles"] = (
            Post.objects
            .filter(
                status=Post.Status.PUBLISHED,
                is_featured=True,
                published_at__isnull=False,
                published_at__lte=timezone.now(),
            )
            .select_related("category")
            .order_by("-published_at")[:5]
        )

        return context



from django.db.models import F
from django.utils import timezone
from django.views.generic import DetailView

from .models import Post


class BlogDetailView(DetailView):
    model = Post
    template_name = "blogs/detail-blog.html"
    context_object_name = "article"

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                status=Post.Status.PUBLISHED,
                published_at__isnull=False,
                published_at__lte=timezone.now(),
            )
            .select_related("user", "category")
            .prefetch_related("tags")
        )

    def get_object(self, queryset=None):
        article = super().get_object(queryset)

        Post.objects.filter(pk=article.pk).update(
            views=F("views") + 1
        )

        article.views += 1
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.category_id:
            context["related_articles"] = (
                Post.objects
                .filter(
                    status=Post.Status.PUBLISHED,
                    published_at__isnull=False,
                    published_at__lte=timezone.now(),
                    category=self.object.category,
                )
                .exclude(pk=self.object.pk)
                .select_related("user", "category")
                .order_by("-published_at")[:4]
            )
        else:
            context["related_articles"] = Post.objects.none()

        return context

