from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from order.models import Order, OrderStatus
from django.views.generic import DetailView


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = "adminpanel/order-list.html"
    context_object_name = "orders"
    paginate_by = 15

    STATUS_TABS = {
        "all": Q(),
        "paid": Q(status=OrderStatus.PAID),
        "shipping": Q(status=OrderStatus.SHIPPED),
        "delivered": Q(status=OrderStatus.DELIVERED),
        "failed": Q(status=OrderStatus.CANCELED),
    }

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        qs = (
            Order.objects
            .select_related("user")
            .only(
                "id", "first_name", "last_name", "final_price",
                "status", "created_at",
                "user__email",
            )
        )

        # تب وضعیت
        status = self.request.GET.get("status", "all")
        if status in self.STATUS_TABS and status != "all":
            qs = qs.filter(self.STATUS_TABS[status])

        # جست‌وجو
        query = self.request.GET.get("q", "").strip()
        if query:
            search_q = (
                    Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(user__email__icontains=query)
                    | Q(phone_number__icontains=query)
            )
            if query.isdigit():
                search_q |= Q(pk=int(query))
            qs = qs.filter(search_q)

        # فیلتر تاریخ
        date_filter = self.request.GET.get("date", "all")
        now = timezone.now()
        if date_filter == "today":
            qs = qs.filter(created_at__date=timezone.localdate(now))
        elif date_filter == "week":
            qs = qs.filter(created_at__gte=now - timedelta(days=7))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        counts = Order.objects.aggregate(
            total=Count("id"),
            paid=Count("id", filter=Q(status=OrderStatus.PAID)),
            shipping=Count("id", filter=Q(status=OrderStatus.SHIPPED)),
            delivered=Count("id", filter=Q(status=OrderStatus.DELIVERED)),
            failed=Count("id", filter=Q(status=OrderStatus.CANCELED)),
        )

        # attach کردن transition به هر سفارش
        for order in context["orders"]:
            order.next_transition = order.get_next_transition()

        context.update({
            "tab_counts": counts,
            "active_status": self.request.GET.get("status", "all"),
            "search_query": self.request.GET.get("q", ""),
            "active_date": self.request.GET.get("date", "all"),
            "result_count": context["paginator"].count if context.get("paginator") else 0,
        })
        return context


class OrderStatusTransitionView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        transition = order.get_next_transition()
        if transition is None:
            return HttpResponseBadRequest(
                "این سفارش در وضعیتی نیست که قابل انتقال باشد."
            )

        new_status, _ = transition

        # به‌روزرسانی اتمیک در برابر race condition
        updated = (
            Order.objects
            .filter(pk=order.pk, status=order.status)
            .update(status=new_status)
        )
        if not updated:
            return HttpResponseBadRequest(
                "وضعیت سفارش تغییر کرده است. صفحه را رفرش کنید."
            )

        return redirect(request.META.get("HTTP_REFERER", "adminpanel:order-list"))


class OrderPrintView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = "adminpanel/order-print.html"
    context_object_name = "order"

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user", "address")
            .prefetch_related("items")
        )
