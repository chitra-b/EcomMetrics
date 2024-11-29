# urls.py

from django.urls import path
from .views import (
    MonthlySalesVolumeView,
    MonthlyRevenueView,
    SalesDataFilterView,
    SummaryMetricsView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="EcomMetrics API",
        default_version="v1",
        description="API documentation for EcomMetrics",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path(
        "api/sales-volume/",
        MonthlySalesVolumeView.as_view(),
        name="monthly_sales_volume",
    ),
    path("api/revenue/", MonthlyRevenueView.as_view(), name="monthly_revenue"),
    path("api/sales-data/", SalesDataFilterView.as_view(), name="sales_data_filter"),
    path("api/summary-metrics/", SummaryMetricsView.as_view(), name="summary_metrics"),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
