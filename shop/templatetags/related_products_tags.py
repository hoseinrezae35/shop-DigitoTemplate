from django import template
from shop.models import Product, ProductFavorite

register = template.Library()


@register.inclusion_tag("include/related_products.html", takes_context=True)
def show_related_products(context, product):

    category_ids = product.category.get_descendant_ids()

    products = list(
        Product.objects
        .select_related("category")
        .filter(
            category_id__in=category_ids,
            is_available=True
        )
        .exclude(pk=product.pk)
        .order_by("-created_at")
    )

    favorite_product_ids = set()

    request = context["request"]

    if request.user.is_authenticated:
        favorite_product_ids = set(
            ProductFavorite.objects.filter(
                user=request.user,
                product_id__in=[p.id for p in products]
            ).values_list("product_id", flat=True)
        )

    return {
        "r_products": products[:8],
        "product": product,
        "favorite_product_ids": favorite_product_ids,
    }
