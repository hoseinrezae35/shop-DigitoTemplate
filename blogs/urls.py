from django.urls import path
from . import views

app_name = "blogs"

urlpatterns = [
    path('blog-list', views.BlogListView.as_view(), name="blog-list"),
    path('blog-detail/<int:pk>', views.BlogDetailView.as_view(), name="blog-detail"),
]