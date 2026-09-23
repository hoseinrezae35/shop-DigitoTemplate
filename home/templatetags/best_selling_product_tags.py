from django import template
from shop.models import Product, Category, ProductFavorite

register = template.Library()


@register.inclusion_tag("include/best_sellers_product.html", takes_context=True)
def show_best_selling_products(context):
    best_sellers = list(Product.objects.filter(is_bestseller=True).order_by("-created_at")[:6])
    favorite_product_ids = set()
    request = context["request"]
    if request.user.is_authenticated:
        favorite_product_ids = set(ProductFavorite.objects.filter(user=request.user,
                                                                  product_id__in=[product.pk for product in
                                                                                  best_sellers]).values_list(
            "product_id", flat=True))
    return {"best_sellers": best_sellers, "favorite_product_ids": favorite_product_ids, }


@register.inclusion_tag(
    "include/new_product.html",
    takes_context=True
)
def show_new_products(context):
    new_product = list(
        Product.objects
        .filter(is_new=True)
        .order_by("-created_at")[:6]
    )

    favorite_product_ids = set()

    request = context["request"]

    if request.user.is_authenticated:
        favorite_product_ids = set(
            ProductFavorite.objects.filter(
                user=request.user,
                product_id__in=[product.pk for product in new_product]
            ).values_list("product_id", flat=True)
        )

    return {
        "new_product": new_product,
        "favorite_product_ids": favorite_product_ids,
    }


@register.inclusion_tag('include/show_category_in_index.html')
def show_category_in_index():
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).order_by('-created_at')[:12]

    return {'categories': categories}
