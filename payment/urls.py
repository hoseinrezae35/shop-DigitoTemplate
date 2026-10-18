from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [

    path("start/<uuid:payment_id>/", views.StartPaymentView.as_view(), name="start"),

    path("zarinpal/callback/", views.ZarinPalCallbackView.as_view(), name="zarinpal-callback"),

    path("result/<uuid:payment_id>/", views.PaymentResultView.as_view(), name="result"),
]
