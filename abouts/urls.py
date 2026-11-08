from django.urls import path
from . import views

app_name = "abouts"

urlpatterns = [
    path('about/', views.AboutPageView.as_view(), name='about-me'),
]
