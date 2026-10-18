from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.db import transaction
from django.utils import timezone
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest

from cart.cart import CartSession
from order.models import OrderStatus, PaymentStatus
from shop.models import Product

from .models import Payment
from .zarinpal import (
    ZarinPalError,
    ZarinPalService,
)


class StartPaymentView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def get(self, request, payment_id, *args, **kwargs):

        payment = get_object_or_404(
            Payment.objects.select_related("order"),
            pk=payment_id,
            order__user=request.user,
        )

        order = payment.order

        # قبلاً پرداخت شده
        if payment.status == PaymentStatus.SUCCESS:
            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        if order.payment_status == PaymentStatus.SUCCESS:
            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        if order.status != OrderStatus.PENDING:
            messages.error(
                request,
                "این سفارش قابل پرداخت نیست.",
            )

            return redirect("order:checkout")

        callback_url = request.build_absolute_uri(
            reverse("payment:zarinpal-callback")
        )

        service = ZarinPalService()

        try:

            result = service.request_payment(
                amount=payment.amount,
                callback_url=callback_url,
                description=f"پرداخت سفارش #{order.pk}",
                mobile=order.phone_number,
            )

        except ZarinPalError as exc:

            payment.status = PaymentStatus.FAILED
            payment.error_message = str(exc)

            payment.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

            messages.error(
                request,
                str(exc),
            )

            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        payment.authority = result["authority"]

        payment.status = PaymentStatus.PENDING

        payment.error_code = ""
        payment.error_message = ""

        payment.save(
            update_fields=[
                "authority",
                "status",
                "error_code",
                "error_message",
                "updated_at",
            ]
        )

        return redirect(
            result["payment_url"]
        )


class ZarinPalCallbackView(View):

    def get(self, request, *args, **kwargs):

        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        # بدون Authority نمی‌توانیم Payment را پیدا کنیم.
        if not authority:
            return HttpResponseBadRequest(
                "شناسه پرداخت از زرین‌پال دریافت نشد."
            )

        payment = (
            Payment.objects
            .select_related("order")
            .filter(authority=authority)
            .first()
        )

        # Authority معتبر نیست یا Payment مربوط پیدا نشد.
        if not payment:
            return HttpResponseBadRequest(
                "پرداخت مربوطه پیدا نشد."
            )

        # پرداخت قبلاً موفق شده است.
        if payment.status == PaymentStatus.SUCCESS:
            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        # کاربر پرداخت را لغو کرده است.
        if status != "OK":
            payment.status = PaymentStatus.FAILED
            payment.error_message = (
                "پرداخت توسط کاربر لغو شد."
            )

            payment.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        service = ZarinPalService()

        try:

            result = service.verify_payment(
                amount=payment.amount,
                authority=payment.authority,
            )

        except ZarinPalError as exc:

            payment.error_message = str(exc)
            payment.save(
                update_fields=[
                    "error_message",
                    "updated_at",
                ]
            )

            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        # نتیجه Verify ناموفق است.
        if not result["success"]:
            payment.status = PaymentStatus.FAILED
            payment.error_code = str(
                result.get("code") or ""
            )
            payment.error_message = (
                    result.get("message")
                    or "پرداخت تأیید نشد."
            )

            payment.save(
                update_fields=[
                    "status",
                    "error_code",
                    "error_message",
                    "updated_at",
                ]
            )

            return redirect(
                "payment:result",
                payment_id=payment.id,
            )

        with transaction.atomic():

            payment = (
                Payment.objects
                .select_for_update()
                .select_related("order")
                .get(pk=payment.pk)
            )

            # جلوگیری از پردازش دوباره Callback
            if payment.status == PaymentStatus.SUCCESS:
                return redirect(
                    "payment:result",
                    payment_id=payment.id,
                )

            order = payment.order

            # تغییر وضعیت پرداخت
            payment.status = PaymentStatus.SUCCESS
            payment.ref_id = str(
                result.get("ref_id") or ""
            )
            payment.paid_at = timezone.now()
            payment.error_code = ""
            payment.error_message = ""

            payment.save(
                update_fields=[
                    "status",
                    "ref_id",
                    "paid_at",
                    "error_code",
                    "error_message",
                    "updated_at",
                ]
            )

            # تغییر وضعیت سفارش
            order.payment_status = PaymentStatus.SUCCESS
            order.status = OrderStatus.PAID

            order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "updated_at",
                ]
            )

            # ثبت فروش محصولات
            for item in order.items.select_for_update().select_related("product"):
                product = item.product

                product.sales += item.quantity

                product.save(
                    update_fields=[
                        "sales",
                        "updated_at",
                    ]
                )

            # بعد از پرداخت موفق، سبد خرید خالی می‌شود
            cart = CartSession(request.session)
            cart.clear()

        return redirect(
            "payment:result",
            payment_id=payment.id,
        )


class PaymentResultView(LoginRequiredMixin, TemplateView):
    login_url = "accounts:login"

    def get(self, request, payment_id, *args, **kwargs):
        payment = get_object_or_404(
            Payment.objects.select_related("order"),
            pk=payment_id,
            order__user=request.user,
        )

        if payment.status == PaymentStatus.SUCCESS:
            return render(
                request,
                "payment/payment-success.html",
                {"payment": payment, "order": payment.order},
            )
        else:
            return render(
                request,
                "payment/payment-failed.html",
                {"payment": payment, "order": payment.order},
            )
