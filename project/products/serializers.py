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
# to reduce the nested depth we create a simplified product serializer for offers
class ProductInOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'image',
            'price',
            'stock'
        ]


class MainOfferSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = MainOffer
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'is_active']

class OfferSerializer(serializers.ModelSerializer):
    campaign = MainOfferSerializer(read_only=True)  # ← nested campaign info
    product = ProductInOfferSerializer(read_only=True)  # ← simplified product info
    


    class Meta:
        model = Offer
        fields = [
            'id', 'new_price', 'old_price', 'percentage_off',
            'campaign', 'product'
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
    display_price=serializers.SerializerMethodField()
    active_offer = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description','display_price',
            'price', 'stock', 'created_at', 'updated_at', 'image',
            'likes_count', 'views_count', 'sizes', 'images', 'offers', 'active_offer'
        ]

    def _get_active_offer_obj(self, product):
        """Return the Offer object if active, else None."""
        now = timezone.now()
        return Offer.objects.filter(
            product=product,
            campaign__start_date__lte=now,
            campaign__end_date__gte=now
        ).select_related('campaign').first()

    def get_display_price(self, obj):
        offer = self._get_active_offer_obj(obj)
        return str(offer.new_price) if offer else str(obj.price)
    def get_active_offer(self, obj):
   
     offer = self._get_active_offer_obj(obj)
     if offer:
        return OfferSerializer(offer, context=self.context).data
     return None



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
        # This method returns a list of subcategories for each categor

        





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

#ADMIN
# For WRITING (CREATE/UPDATE) - accepts ID only
class SubCategoryWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category']
        # NO depth = 1 here to avoid nested representation during write operations
        #LESSON LEANT JUST WRITEDIFF SERIALIZS FO RREAR WRITE,THEONE FOR READCAN CONTAIN FULL OBJECTS WHILE THE WRITE ONE ONLY IDS


#FRO WRITING PRODCTS
class ProductWriteSerializer(serializers.ModelSerializer):
    subcategory=serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all()
    
    )
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'stock', 'image', 'subcategory'
        ]


#FOR ADMIN OFFER WRITE
class OfferWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    campaign = serializers.PrimaryKeyRelatedField(
        queryset=MainOffer.objects.all()
    )
    class Meta:
        model = Offer
        fields = [
            'id', 'new_price', 'old_price', 'percentage_off',
            'campaign', 'product'
        ]