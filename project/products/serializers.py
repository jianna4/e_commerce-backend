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
    subcategories = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at', 'subcategories']
        # This method returns a list of subcategories for each category
    def get_subcategories(self, obj):
        return [{"id": sub.id, "name": sub.name} for sub in obj.subcategories.all()]



# --------------------
# ProductColor Serializer
# --------------------
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'name', 'hex_code']


# --------------------
# ProductImage Serializer
# --------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']



# ----------------------
# Product Serializer
# ----------------------



class ProductSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'subcategory',
            'stock', 'available', 'created_at', 'updated_at', 'image',
            'size', 'likes_count', 'views_count', 'is_active', 'colors', 'images'
        ]


# ----------------------
# SubCategory Serializer
# ----------------------


class SubCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)  # <-- add this line or do asin the categoryto nestsubcategories

    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'products']




class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # Read-only fields for frontend display
    product_detail = ProductSerializer(source='product', read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'size', 'color', 'price', 'total']

    def create(self, validated_data):
        product = validated_data['product']
        # Set price from product automatically
        validated_data['price'] = product.price
        # total will be calculated in model's save method
        return super().create(validated_data)


# --------------------
# Order Serializer
# --------------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # automatically set in view

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'updated_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # update order total_price after adding items
        order.update_total_price()
        return order
