from rest_framework import serializers
from .models import Order, Customer, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    delivery_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id",
            "product_name",
            "category",
            "quantity_sold",
            "total_sale_value",
            "date_of_sale",
            "platform_name",
            "state",
            "delivery_status",
        ]

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_category(self, obj):
        return obj.product.category

    def get_platform_name(self, obj):
        return obj.platform.name

    def get_state(self, obj):
        return obj.delivery.delivery_address.state if obj.delivery else None

    def get_delivery_status(self, obj):
        return obj.delivery.delivery_status if obj.delivery else None


class MonthlySalesVolumeSerializer(serializers.Serializer):
    month = serializers.DateField(format="%Y-%m")  # Year-Month format
    total_quantity_sold = serializers.IntegerField()


class MonthlyRevenueSerializer(serializers.Serializer):
    month = serializers.DateField(format="%Y-%m")  # Year-Month format
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)


class SummaryMetricsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_products_sold = serializers.IntegerField()
    canceled_order_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
