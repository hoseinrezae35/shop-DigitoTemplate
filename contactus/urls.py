from django.urls import path
from . import views

app_name = "contactus"

urlpatterns = [
    path('contact/', views.ContactUsView.as_view(), name='contact'),
]
