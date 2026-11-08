from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order-list"),
    path("<int:pk>/transition/", views.OrderStatusTransitionView.as_view(), name="order-transition"),
    path("<int:pk>/print/", views.OrderPrintView.as_view(), name="order-print"),
]
