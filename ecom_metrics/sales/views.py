# views.py
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from .serializers import (
    MonthlySalesVolumeSerializer,
    MonthlyRevenueSerializer,
    OrderSerializer,
)
from .models import Order, Delivery
from .serializers import SummaryMetricsSerializer


import csv
from io import StringIO
from datetime import datetime
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Custom pagination class to handle large result sets
class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page (you can adjust this as needed)
    page_size_query_param = "page_size"
    max_page_size = (
        100  # Limit the max number of items to avoid excessive data fetching
    )


class SalesDataFilterView(APIView):

    def generate_csv(self, orders):
        # Create an in-memory string buffer to write CSV data
        output = StringIO()
        writer = csv.writer(output)

        # Define the CSV header
        writer.writerow(
            [
                "Order ID",
                "Product",
                "Customer",
                "Quantity Sold",
                "Selling Price",
                "Total Sale Value",
                "Date of Sale",
                "Platform",
                "State",
                "Delivery Status",
            ]
        )

        # Write the order data to CSV
        for order in orders:
            writer.writerow(
                [
                    order.order_id,
                    order.product.product_name,
                    order.customer.customer_name,
                    order.quantity_sold,
                    order.selling_price,
                    order.total_sale_value,
                    order.date_of_sale,
                    order.platform.name,
                    order.delivery.delivery_address.state if order.delivery else "N/A",
                    order.delivery.delivery_status if order.delivery else "N/A",
                ]
            )

        # Get the CSV data from the StringIO buffer
        output.seek(0)

        # Create the HTTP response with the CSV file as an attachment
        response = HttpResponse(output, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sales_data.csv"'
        return response

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "date_from",  # Query parameter name
                openapi.IN_QUERY,  # Parameter location (query)
                description="Start date for filtering orders (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "date_to",
                openapi.IN_QUERY,
                description="End date for filtering orders (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Category of the product to filter by",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "delivery_status",
                openapi.IN_QUERY,
                description="Status of delivery to filter orders",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "platform",
                openapi.IN_QUERY,
                description="Platform to filter orders by",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="State to filter delivery address by",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "export_csv",
                openapi.IN_QUERY,
                description="Flag to export the data as CSV (true/false)",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ]
    )
    def get(self, request):
        # Get filter parameters from query parameters
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        category = request.GET.get("category")
        delivery_status = request.GET.get("delivery_status")
        platform = request.GET.get("platform")
        state = request.GET.get("state")
        export_csv = request.GET.get("export_csv", False)  # Check for CSV export

        filters = Q()

        # Apply filters conditionally
        if date_from:
            try:
                date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
                filters &= Q(date_of_sale__gte=date_from)
            except ValueError:
                return Response(
                    {"error": "Invalid date_from format, expected YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if date_to:
            try:
                date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
                filters &= Q(date_of_sale__lte=date_to)
            except ValueError:
                return Response(
                    {"error": "Invalid date_to format, expected YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if category:
            filters &= Q(product__category__icontains=category)

        if delivery_status:
            filters &= Q(delivery__delivery_status=delivery_status)

        if platform:
            filters &= Q(platform__name__icontains=platform)

        if state:
            filters &= Q(delivery__delivery_address__state__icontains=state)

        # Filter orders based on the constructed filters
        orders = Order.objects.filter(filters).select_related(
            "product", "platform", "delivery__delivery_address"
        )

        # Apply pagination
        paginator = CustomPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)

        if export_csv:  # Check if the user wants to export data as CSV
            # Generate CSV response
            return self.generate_csv(orders)

        # Serialize the filtered and paginated orders
        serializer = OrderSerializer(paginated_orders, many=True)

        return paginator.get_paginated_response(serializer.data)


# class SalesDataFilterView(APIView):
#
#     def get(self, request):
#         # Get filter parameters from query parameters
#         date_from = request.GET.get("date_from")
#         date_to = request.GET.get("date_to")
#         category = request.GET.get("category")
#         delivery_status = request.GET.get("delivery_status")
#         platform = request.GET.get("platform")
#         state = request.GET.get("state")
#
#         filters = Q()
#
#         # Apply filters conditionally
#         if date_from:
#             try:
#                 date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
#                 filters &= Q(date_of_sale__gte=date_from)
#             except ValueError:
#                 return Response(
#                     {"error": "Invalid date_from format, expected YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#         if date_to:
#             try:
#                 date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
#                 filters &= Q(date_of_sale__lte=date_to)
#             except ValueError:
#                 return Response(
#                     {"error": "Invalid date_to format, expected YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#         if category:
#             filters &= Q(product__category__icontains=category)
#
#         if delivery_status:
#             filters &= Q(delivery__delivery_status=delivery_status)
#
#         if platform:
#             filters &= Q(platform__name__icontains=platform)
#
#         if state:
#             filters &= Q(delivery__delivery_address__state__icontains=state)
#
#         # Filter orders based on the constructed filters
#         orders = Order.objects.filter(filters)
#
#         # Serialize the filtered orders
#         serializer = OrderSerializer(orders, many=True)
#
#         return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlySalesVolumeView(APIView):
    """
    API to get the monthly sales volume (Quantity Sold).
    """

    def get(self, request, *args, **kwargs):
        # Aggregate total quantity sold by month
        sales_data = (
            Order.objects.annotate(month=TruncMonth("date_of_sale"))
            .values("month")
            .annotate(total_quantity_sold=Sum("quantity_sold"))
            .order_by("month")
        )

        # Serialize the data
        serializer = MonthlySalesVolumeSerializer(sales_data, many=True)

        return Response(serializer.data)


class MonthlyRevenueView(APIView):
    """
    API to get the monthly revenue (Total Sale Value).
    """

    def get(self, request, *args, **kwargs):
        # Aggregate total sale value by month
        revenue_data = (
            Order.objects.annotate(month=TruncMonth("date_of_sale"))
            .values("month")
            .annotate(total_revenue=Sum("total_sale_value"))
            .order_by("month")
        )

        # Serialize the data
        serializer = MonthlyRevenueSerializer(revenue_data, many=True)

        return Response(serializer.data)


class SummaryMetricsView(APIView):
    def get(self, request):
        # Calculate Total Revenue (sum of total_sale_value from all orders)
        total_revenue = (
            Order.objects.aggregate(total_revenue=Sum("total_sale_value"))[
                "total_revenue"
            ]
            or 0
        )

        # Calculate Total Orders (count of all orders)
        total_orders = Order.objects.count()

        # Calculate Total Products Sold (sum of quantity_sold from all orders)
        total_products_sold = (
            Order.objects.aggregate(total_products_sold=Sum("quantity_sold"))[
                "total_products_sold"
            ]
            or 0
        )

        # Calculate Canceled Order Percentage
        total_canceled_orders = Delivery.objects.filter(
            delivery_status="Cancelled"
        ).count()
        canceled_order_percentage = (
            (total_canceled_orders / total_orders * 100) if total_orders > 0 else 0
        )

        # Prepare the data
        metrics_data = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_products_sold": total_products_sold,
            "canceled_order_percentage": canceled_order_percentage,
        }

        # Serialize and return the response
        serializer = SummaryMetricsSerializer(metrics_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
