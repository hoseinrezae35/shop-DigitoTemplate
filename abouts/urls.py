from django.urls import path
from . import views

app_name = "abouts"

urlpatterns = [
    path('about-me/', views.AboutMeView.as_view(), name='about-me'),
]
