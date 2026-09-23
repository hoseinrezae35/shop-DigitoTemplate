from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from accounts.models import User
from .models import Product, Category, ProductComment, ProductFavorite


class ProductListView(ListView):
    template_name = 'shop/product-list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_product_ids = set()
        if self.request.user.is_authenticated:
            favorite_product_ids = set(ProductFavorite.objects.filter(user=self.request.user,
                                                                      product_id__in=self.object_list.values_list(
                                                                          "id",
                                                                          flat=True)).values_list(
                "product_id", flat=True))

        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        query_params.pop('category', None)
        context['query_string'] = query_params.urlencode()

        context["product"] = Product.objects.filter(is_available=True)
        context['category'] = Category.objects.filter(parent=None, is_active=True)
        context['total_items'] = self.get_queryset().count()
        context["favorite_product_ids"] = favorite_product_ids

        return context

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        search_q = self.request.GET.get("q", "").strip()

        if search_q:
            category_ids = Category.search_category_ids(search_q)
            queryset = queryset.filter(

                Q(name__icontains=search_q) |
                Q(short_description__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(sku__icontains=search_q) |
                Q(category__name__icontains=search_q) |
                Q(category_id__in=category_ids)

            ).distinct()

        if min_price := self.request.GET.get('min_price'):
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price := self.request.GET.get('max_price'):
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        if self.request.GET.get('only_available'):
            queryset = queryset.filter(stock__gt=0)

        if category_slug := self.request.GET.get('category'):
            category = Category.objects.filter(slug=category_slug, is_active=True).first()
            if category:
                category_ids = category.get_descendant_ids()
                queryset = queryset.filter(category_id__in=category_ids)

        sort = self.request.GET.get('sort', 'all_product')

        if sort == 'bestseller':
            queryset = queryset.filter(is_bestseller=True)
        if sort == 'featured':
            queryset = queryset.filter(is_featured=True)
        elif sort == 'cheapest':
            queryset = queryset.order_by('price')
        elif sort == 'expensive':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')

        return queryset


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product-detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.prefetch_related(
            "comments__user"
        ).filter(
            is_available=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["comments"] = self.object.comments.filter(
            is_active=True
        )

        context["is_favorite"] = False

        if self.request.user.is_authenticated:
            context["is_favorite"] = ProductFavorite.objects.filter(
                user=self.request.user,
                product=self.object
            ).exists()

        return context


class CategoryDetailView(ListView):
    model = Product
    template_name = "shop/product-list.html"
    paginate_by = 20

    def get_queryset(self):
        category = get_object_or_404(Category, id=self.kwargs["pk"])

        queryset = Product.objects.filter(
            category_id__in=category.get_descendant_ids(),
            is_available=True,
        )

        if search_q := self.request.GET.get('q'):
            queryset = queryset.filter(
                Q(name__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(short_description__icontains=search_q) |
                Q(category__name__icontains=search_q)
            )

        if min_price := self.request.GET.get('min_price'):
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price := self.request.GET.get('max_price'):
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        if self.request.GET.get('only_available'):
            queryset = queryset.filter(stock__gt=0)

        if category_slug := self.request.GET.get('category'):
            category = Category.objects.filter(slug=category_slug, is_active=True).first()
            if category:
                category_ids = category.get_descendant_ids()
                queryset = queryset.filter(category_id__in=category_ids)

        sort = self.request.GET.get('sort', 'all_product')

        if sort == 'bestseller':
            queryset = queryset.filter(is_bestseller=True)
        elif sort == 'cheapest':
            queryset = queryset.order_by('price')
        elif sort == 'expensive':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        favorite_product_ids = set()
        if self.request.user.is_authenticated:
            favorite_product_ids = set(ProductFavorite.objects.filter(user=self.request.user,
                                                                      product_id__in=self.object_list.values_list(
                                                                          "id",
                                                                          flat=True)).values_list(
                "product_id", flat=True))
        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context["query_string"] = query_params.urlencode()
        context["total_items"] = self.object_list.count()
        context['favorite_product_ids'] = favorite_product_ids

        return context


class AddProductCommentView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        product = get_object_or_404(
            Product,
            pk=kwargs["pk"],
            is_available=True
        )

        text = request.POST.get("text", "").strip()
        recommendation = request.POST.get("recommendation", "").strip()

        if not text:
            return JsonResponse({
                "status": "error",
                "message": "لطفاً متن دیدگاه را وارد کنید."
            }, status=400)

        if recommendation not in [
            ProductComment.Recommendation.RECOMMENDED,
            ProductComment.Recommendation.NOT_RECOMMENDED
        ]:
            return JsonResponse({
                "status": "error",
                "message": "لطفاً پیشنهاد یا عدم پیشنهاد را انتخاب کنید."
            }, status=400)

        comment = ProductComment.objects.create(
            product=product,
            user=request.user,
            text=text,
            recommendation=recommendation
        )

        return JsonResponse({
            "status": "success",
            "message": "دیدگاه شما با موفقیت ثبت شد و پس از برسی نمایش داده خواهد شد.",
            "comment": {
                "id": comment.id,
                "title": comment.title,
                "text": comment.text,
                "recommendation": comment.recommendation,
                "recommendation_display": comment.get_recommendation_display(),
                "user": request.user.email,
                "created_at": comment.created_at.strftime("%Y/%m/%d")
            }
        })


class ToggleProductFavoriteView(LoginRequiredMixin, View):

    def handle_no_permission(self):
        return JsonResponse({
            "status": "error",
            "message": "برای افزودن محصول به علاقه‌مندی‌ها ابتدا وارد حساب کاربری شوید."
        }, status=401)

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(
            Product,
            pk=kwargs["pk"],
            is_available=True
        )

        favorite = ProductFavorite.objects.filter(
            user=request.user,
            product=product
        ).first()

        if favorite:
            favorite.delete()

            return JsonResponse({
                "status": "success",
                "action": "removed",
                "message": "محصول با موفقیت از علاقه‌مندی‌ها برداشته شد.",
            })

        ProductFavorite.objects.create(
            user=request.user,
            product=product
        )

        return JsonResponse({
            "status": "success",
            "action": "added",
            "message": "محصول با موفقیت به علاقه‌مندی‌ها اضافه شد.",
        })


from django.views.generic import ListView
from django.db.models import Q

from .models import Product, ProductFavorite, Category


class RelatedProductsListView(ListView):
    template_name = "shop/product-list.html"
    paginate_by = 20

    def get_queryset(self):

        self.current_product = get_object_or_404(
            Product.objects.select_related("category"),
            pk=self.kwargs["pk"],
            is_available=True
        )

        category_ids = self.current_product.category.get_descendant_ids()

        queryset = (
            Product.objects
            .filter(
                category_id__in=category_ids,
                is_available=True
            )
            .exclude(pk=self.current_product.pk)
        )

        search_q = self.request.GET.get("q", "").strip()

        if search_q:
            search_category_ids = Category.search_category_ids(search_q)

            queryset = queryset.filter(
                Q(name__icontains=search_q) |
                Q(short_description__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(sku__icontains=search_q) |
                Q(category__name__icontains=search_q) |
                Q(category_id__in=search_category_ids)
            ).distinct()

        if min_price := self.request.GET.get("min_price"):
            try:
                queryset = queryset.filter(
                    price__gte=float(min_price)
                )
            except ValueError:
                pass

        if max_price := self.request.GET.get("max_price"):
            try:
                queryset = queryset.filter(
                    price__lte=float(max_price)
                )
            except ValueError:
                pass

        if self.request.GET.get("only_available"):
            queryset = queryset.filter(stock__gt=0)

        if category_slug := self.request.GET.get("category"):
            category = Category.objects.filter(
                slug=category_slug,
                is_active=True
            ).first()

            if category:
                category_ids = category.get_descendant_ids()

                queryset = queryset.filter(
                    category_id__in=category_ids
                )

        sort = self.request.GET.get("sort", "all_product")

        if sort == "bestseller":
            queryset = queryset.filter(
                is_bestseller=True
            )

        elif sort == "featured":
            queryset = queryset.filter(
                is_featured=True
            )

        elif sort == "cheapest":
            queryset = queryset.order_by("price")

        elif sort == "expensive":
            queryset = queryset.order_by("-price")

        elif sort == "newest":
            queryset = queryset.order_by("-created_at")

        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        favorite_product_ids = set()

        if self.request.user.is_authenticated:
            favorite_product_ids = set(
                ProductFavorite.objects.filter(
                    user=self.request.user,
                    product_id__in=self.object_list.values_list(
                        "id",
                        flat=True
                    )
                ).values_list(
                    "product_id",
                    flat=True
                )
            )

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        query_params.pop("category", None)

        context["query_string"] = query_params.urlencode()

        context["product"] = self.object_list

        context["category"] = Category.objects.filter(
            parent=None,
            is_active=True
        )

        context["total_items"] = self.get_queryset().count()

        context["favorite_product_ids"] = favorite_product_ids

        return context
