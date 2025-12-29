from rest_framework import serializers
from .models import (
    Category,
    SubCategory,
    Product,
    productsizes ,
    ProductSizeColor,
    ProductImage,
    Offer,
    MainOffer,
    Order,
    OrderItem,
)
from django.utils import timezone


#offer serializer
class OfferSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'product', 'product_name', 'new_price',
            'old_price', 'percentage_off', 'campaign', 'campaign_title'
        ]


class MainOfferSerializer(serializers.ModelSerializer):
    offers = OfferSerializer(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = MainOffer
        fields = [
            'id', 'title', 'description', 'start_date',
            'end_date', 'is_active', 'offers'
        ]


# --------------------
# ProductColor Serializer
# --------------------
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSizeColor
        fields = ['id', 'color_name', 'hex_code', 'quantity']


# --------------------
# ProductImage Serializer
# --------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']




#productsizes serializer

class ProductSizeSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(many=True, read_only=True)
    class Meta:
        model = productsizes
        fields = ['id', 'waist_shoe_size','hips', 'height','colors']


#product serializer

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)

    display_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 
            'stock', 'created_at', 'updated_at', 'image',
            'likes_count', 'views_count', 'sizes', 'images', 'offers'
        ]

    def _get_active_offer(self, product):
        """
        Helper: Returns the first active Offer for this product,
        based on current time and campaign dates.
        """
        now = timezone.now()
        return Offer.objects.filter(
            product=product,
            campaign__start_date__lte=now,
            campaign__end_date__gte=now
        ).first()

    def get_display_price(self, obj):
        """
        Returns the sale price if an active offer exists,
        otherwise returns the regular product price.
        Output as string to preserve decimal format in JSON.
        """
        active_offer = self._get_active_offer(obj)
        if active_offer:
            return str(active_offer.new_price)
        return str(obj.price)

    def get_discount_percentage(self, obj):
        """
        Returns the discount percentage if an active offer exists,
        otherwise returns 0.
        """
        active_offer = self._get_active_offer(obj)
        if active_offer:
            return active_offer.percentage_off
        return 0



# ----------------------
# SubCategory Serializer
# ----------------------


class SubCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)  # <-- add this line or do asin the categoryto nestsubcategories

    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'products']
        depth = 1  # This will include related objects with their basic fields


# ----------------------
# Category Serializer
# ----------------------
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at', 'subcategories']
        # This method returns a list of subcategories for each category





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
