from rest_framework import serializers
from .models import (
    Category,
    SubCategory,
    Product,
    ProductColor,
    ProductImage,
    Order,
    OrderItem
)

# ----------------------
# Category Serializer
# ----------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']

# ----------------------
# SubCategory Serializer
# ----------------------
class SubCategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()  # We'll populate products under this subcategory

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'products']

    def get_products(self, obj):
        return ProductSerializer(obj.products.all(), many=True).data

# ----------------------
# Product Serializer
# ----------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'image', 'stock', 'available']

# ----------------------
# Category Detail Serializer (with hierarchy)
# ----------------------
class CategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'subcategories']

from rest_framework import serializers
from .models import Order, OrderItem, Product

class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product"
    )

    class Meta:
        model = OrderItem
        fields = [
            "product_id",
            "quantity"
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "price"
        ]
class OrderSerializer(serializers.ModelSerializer):
    # input (add to cart)
    items = OrderItemCreateSerializer(
        many=True,
        write_only=True
    )

    # output (cart popup / order summary)
    order_items = OrderItemSerializer(
        many=True,
        read_only=True,
        source="items"
    )

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total_price",
            "created_at",
            "updated_at",
            "items",
            "order_items"
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(
            user=user,
            status="pending"
        )

        total_price = 0

        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            total_price += product.price * quantity

        order.total_price = total_price
        order.save()

        return order

