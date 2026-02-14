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
from mainapp.models import User


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
    is_active = serializers.ReadOnlyField()
    


    class Meta:
        model = Offer
        fields = [
            'id', 'new_price', 'old_price', 'percentage_off',
            'campaign', 'product', 'is_active'
        ]
    

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSizeColor
        fields = ['id', 'color_name', 'hex_code', 'quantity']



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']





class ProductSizeSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(many=True, read_only=True)
    class Meta:
        model = productsizes
        fields = ['id', 'waist_shoe_size','hips', 'height','colors']



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




class SubCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)  # <-- add this line or do asin the categoryto nestsubcategories

    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'products']
        depth = 1  # This will include related objects with their basic fields



class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at', 'subcategories']
        # This method returns a list of subcategories for each categor

 


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product_variant.product_size.product.name",
        read_only=True
    )
    size = serializers.CharField(
        source="product_variant.product_size.waist_shoe_size",
        read_only=True
    )
    color = serializers.CharField(
        source="product_variant.color_name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_variant",
            "product_name",
            "size",
            "color",
            "quantity",
            "price",
            "total",
        ]
        read_only_fields = ["price", "total"]



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)


    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "created_at",
            "items",
        ]
        read_only_fields = ["total_price", "created_at"]



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
    

class ProductReadSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'stock', 'image',
            'category', 'subcategory'
        ]

    def get_category(self, obj):
        if obj.subcategory:
            return {
                "id": obj.subcategory.category.id,
                "name": obj.subcategory.category.name
            }
        return None
    def get_subcategory(self, obj):
        if obj.subcategory:
            return {
                "id": obj.subcategory.id,
                "name": obj.subcategory.name
            }
        return None

#FOR ADMIN OFFER WRITE
class OfferWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    campaign = serializers.PrimaryKeyRelatedField(
        queryset=MainOffer.objects.all()
    )
    is_active = serializers.ReadOnlyField()
    class Meta:
        model = Offer
        fields = [
            'id', 'new_price', 'old_price', 'percentage_off',
            'campaign', 'product', 'is_active'
        ]


#write product details
    

class ProductColorSerializerwrite(serializers.ModelSerializer):
    product_size= serializers.PrimaryKeyRelatedField(
        queryset= productsizes.objects.all()
    )
    class Meta:
        model = ProductSizeColor
        fields = ['id','product_size', 'color_name', 'hex_code', 'quantity']



class ProductImageSerializerwrite(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    class Meta:
        model = ProductImage
        fields = ['id','product', 'image']





class ProductSizeSerializerwrite(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    class Meta:
        model = productsizes
        fields = ['id', 'waist_shoe_size','hips', 'height', 'product']

