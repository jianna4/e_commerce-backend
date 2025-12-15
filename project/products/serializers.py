from rest_framework import serializers
from .models import Category, SubCategory, Product

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

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'updated_at', 'items']
