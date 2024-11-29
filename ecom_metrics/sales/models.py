from django.db import models


class Platform(models.Model):
    platform_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.CharField(max_length=15, primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.product_name


class Customer(models.Model):
    customer_id = models.CharField(max_length=15, primary_key=True)
    customer_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.customer_name


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    street = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, db_index=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.pin_code}"


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=15)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    quantity_sold = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_sale_value = models.DecimalField(max_digits=15, decimal_places=2)
    date_of_sale = models.DateField(db_index=True)
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="orders"
    )
    seller_id = models.CharField(max_length=100, db_index=True)
    additional_data = models.JSONField(
        blank=True, null=True
    )  # To store platform-specific fields

    class Meta:
        unique_together = (
            "order_id",
            "product",
        )

    def __str__(self):
        return f"Order {self.order_id}"


class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ("Delivered", "Delivered"),
        ("In Transit", "In Transit"),
        ("Cancelled", "Cancelled"),
    ]

    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery"
    )
    delivery_address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="deliveries"
    )
    delivery_date = models.DateField(db_index=True)
    delivery_status = models.CharField(
        max_length=20, choices=DELIVERY_STATUS_CHOICES, db_index=True
    )
    delivery_partner = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.order.order_id} - {self.delivery_status}"
