from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta

from cart.cart import CartSession
from dashboard.models import UserAddressModel
from shop.models import Product
from order.models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    ShippingMethod,
)
from payment.models import Payment, PaymentGateway





class OrderView(TemplateView):
    template_name = "order/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = CartSession(self.request.session)

        cart_total = cart.get_total_payment_amount()
        tax_percent = 10
        tax_amount = int(cart_total * tax_percent / 100)
        shipping_cost = 0

        context["cart_total"] = cart_total
        context["tax_percent"] = tax_percent
        context["tax_amount"] = tax_amount
        context["shipping_cost"] = shipping_cost
        context["final_price"] = (
                cart_total
                + tax_amount
                + shipping_cost
        )

        return context


class CreateOrderView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, *args, **kwargs):

        address_id = request.POST.get("address_id")

        if not address_id:
            messages.error(
                request,
                "لطفاً یک آدرس برای ارسال انتخاب کنید.",
            )
            return redirect("order:checkout")

        address = get_object_or_404(
            UserAddressModel,
            pk=address_id,
            user=request.user,
        )

        shipping_method = request.POST.get("shipping_method")

        if shipping_method not in ShippingMethod.values:
            messages.error(
                request,
                "روش ارسال انتخاب شده معتبر نیست.",
            )
            return redirect("order:checkout")

        cart = CartSession(request.session)

        cart_items = cart.get_cart_item()

        if not cart_items:
            messages.error(
                request,
                "سبد خرید شما خالی است.",
            )
            return redirect("cart:cart_list")

        total_price = sum(
            item["total_price"]
            for item in cart_items
        )

        tax_percent = 10

        tax_amount = int(
            total_price * tax_percent / 100
        )

        if shipping_method == ShippingMethod.PICKUP:
            shipping_cost = 0

        elif shipping_method == ShippingMethod.TIPAX:
            shipping_cost = 0

        else:
            shipping_cost = 0

        final_price = (
            total_price
            + tax_amount
            + shipping_cost
        )

        try:

            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,

                    address=address,

                    first_name=address.first_name,
                    last_name=address.last_name,
                    phone_number=address.phone_number,
                    state=address.state,
                    city=address.city,
                    postal_code=address.postal_code,
                    shipping_address=address.address,

                    shipping_method=shipping_method,

                    total_price=total_price,
                    tax_percent=tax_percent,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    final_price=final_price,

                    status=OrderStatus.PENDING,
                    payment_status=PaymentStatus.PENDING,

                    payment_expires_at=timezone.now()
                    + timedelta(minutes=60),
                )

                for item in cart_items:

                    product_id = item["product_obj"].id
                    quantity = item["quantity"]

                    product = (
                        Product.objects
                        .select_for_update()
                        .get(pk=product_id)
                    )

                    if (
                        not product.is_available
                        or product.stock < quantity
                    ):
                        raise ValueError(
                            f"موجودی محصول «{product.name}» کافی نیست."
                        )

                    unit_price = product.final_price

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=unit_price,
                        quantity=quantity,
                        total_price=unit_price * quantity,
                    )

                    product.stock -= quantity

                    if product.stock == 0:
                        product.is_available = False

                    product.save(
                        update_fields=[
                            "stock",
                            "is_available",
                            "sales",
                            "updated_at",
                        ]
                    )

                # تومان → ریال
                payment_amount = order.final_price * 10

                payment = Payment.objects.create(
                    order=order,
                    gateway=PaymentGateway.ZARINPAL,
                    amount=payment_amount,
                    status=PaymentStatus.PENDING,
                )


        except ValueError as exc:

            messages.error(
                request,
                str(exc),
            )

            return redirect("order:checkout")

        return redirect(
            "payment:start",
            payment_id=payment.id,
        )
