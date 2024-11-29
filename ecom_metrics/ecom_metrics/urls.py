# project_name/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin panel URL
    path("", include("sales.urls")),  # Include URLs from your app
]
