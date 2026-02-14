from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Category, SubCategory, Product, Order , Offer ,MainOffer,productsizes,ProductSizeColor,ProductImage
from .serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ProductSerializer,
    OrderSerializer,
    OfferSerializer,
    MainOfferSerializer,
    SubCategoryWriteSerializer,
    ProductWriteSerializer,
    OfferWriteSerializer,
    ProductReadSerializer,
    ProductColorSerializerwrite,
    ProductImageSerializerwrite,
    ProductSizeSerializerwrite,
)
from django.utils import timezone
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser




# Categories

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug, is_active=True)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(category)
    return Response(serializer.data)


# Subcategories

@api_view(['GET'])
@permission_classes([AllowAny])
def subcategory_list(request):
    subcategories = SubCategory.objects.all()
    serializer = SubCategorySerializer(subcategories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def subcategory_detail(request, pk):
    try:
        subcategory = SubCategory.objects.get(pk=pk)
    except SubCategory.DoesNotExist:
        return Response({"detail": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubCategorySerializer(subcategory)
    return Response(serializer.data)


# Products

@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.filter(available=True)
    # Optional filtering by category or subcategory via query params
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    if category_id:
        products = products.filter(subcategory__category__id=category_id)
    if subcategory_id:
        products = products.filter(subcategory__id=subcategory_id)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk, available=True)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductSerializer(product)
    return Response(serializer.data)


#active offers
@api_view(['GET'])
@permission_classes([AllowAny])
def active_offers(request):
    now = timezone.now()

    offers = Offer.objects.filter(
        campaign__start_date__lte=now,
        campaign__end_date__gte=now
    ).select_related(
        'campaign',
        'product'
    )

    serializer = OfferSerializer(offers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#active offers by campaign
@api_view(['GET'])
@permission_classes([AllowAny])
def offers_by_campaign(request):
    now = timezone.now()

    offers = Offer.objects.filter(
        campaign__start_date__lte=now,
        campaign__end_date__gte=now
    ).select_related('campaign', 'product')

    grouped = {}

    for offer in offers:
        campaign = offer.campaign
        key = campaign.id

        if key not in grouped:
            grouped[key] = {
                "campaign": MainOfferSerializer(campaign).data,
                "offers": []
            }

        grouped[key]["offers"].append(
            OfferSerializer(offer).data
        )

    return Response(grouped.values(), status=status.HTTP_200_OK)


# --------------------
# Orders
# --------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_create(request):
    data = request.data.copy()
    data['user'] = request.user.id  # attach logged-in user
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Now for the admin sector 

#CATEGORY LIST
@api_view(['POST','GET','PUT','DELETE','PATCH'])
@parser_classes([MultiPartParser, FormParser])
#@permission_classes([IsAuthenticated])
def category_insertion(request, pk=None):
    
    if request.method == 'GET':
        if pk:
            try:
                category = Category.objects.get(pk=pk)
                serializer = CategorySerializer(category)
                return Response(serializer.data)
            except Category.DoesNotExist:
                return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
    elif request.method == 'POST':
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    elif request.method in ['PUT', 'PATCH']:
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = CategorySerializer(category, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#subcategory list
@api_view(['POST','GET','PUT','DELETE','PATCH'])
#@permission_classes([IsAuthenticated])
def sub_category_insertion(request ,pk=None):
    if request.method == 'POST':
        data=request.data.copy()
        #data['user']= request.user.id
        serializer= SubCategoryWriteSerializer(data=data)
        if serializer.is_valid():
         serializer.save()
         return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        if pk:
            try:
                category = SubCategory.objects.get(pk=pk)
                serializer = SubCategoryWriteSerializer(category)
                return Response(serializer.data)
            except SubCategory.DoesNotExist:
                return Response({"detail": "SubCategory not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = SubCategory.objects.all()
            serializer = SubCategoryWriteSerializer(categories, many=True)
            return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        try:
            category = SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return Response({"detail": "SubCategory not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = SubCategoryWriteSerializer(category, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            category = SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return Response({"detail": "SubCategory not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




    
#product insertion
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST','GET','PUT','DELETE','PATCH'])
#@permission_classes([IsAuthenticated])
def Product_insertion(request, pk=None):
    if request.method == 'POST':
        data=request.data.copy()
        #data['user']= request.user.id
        serializer= ProductWriteSerializer(data=data)
        if serializer.is_valid():
         serializer.save()
         return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        if pk:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductReadSerializer(product)
                return Response(serializer.data)
            except Product.DoesNotExist:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = Product.objects.all()
            serializer = ProductReadSerializer(categories, many=True)
            return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = ProductWriteSerializer(product, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


#productimagewirte

@parser_classes([MultiPartParser, FormParser])
@api_view(['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
def Product_Image_insertion(request, pk=None):

    # CREATE
    if request.method == 'POST':
        serializer = ProductImageSerializerwrite(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # READ
    if request.method == 'GET':
        if pk:
            try:
                image = ProductImage.objects.get(pk=pk)
                serializer = ProductImageSerializerwrite(image)
                return Response(serializer.data)
            except ProductImage.DoesNotExist:
                return Response({"detail": "Product image not found"}, status=status.HTTP_404_NOT_FOUND)

        images = ProductImage.objects.all()
        serializer = ProductImageSerializerwrite(images, many=True)
        return Response(serializer.data)

    # UPDATE
    if request.method in ['PUT', 'PATCH']:
        try:
            image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Product image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductImageSerializerwrite(
            image,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if request.method == 'DELETE':
        try:
            image = ProductImage.objects.get(pk=pk)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Product image not found"}, status=status.HTTP_404_NOT_FOUND)


#product sizes write
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
def Product_size_insertion(request, pk=None):

    # CREATE
    if request.method == 'POST':
        serializer = ProductSizeSerializerwrite(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # READ
    if request.method == 'GET':
        if pk:
            try:
                size = productsizes.objects.get(pk=pk)
                serializer = ProductSizeSerializerwrite(size)
                return Response(serializer.data)
            except productsizes.DoesNotExist:
                return Response({"detail": "Product size not found"}, status=status.HTTP_404_NOT_FOUND)

        sizes = productsizes.objects.all()
        serializer = ProductSizeSerializerwrite(sizes, many=True)
        return Response(serializer.data)

    # UPDATE
    if request.method in ['PUT', 'PATCH']:
        try:
            size = productsizes.objects.get(pk=pk)
        except productsizes.DoesNotExist:
            return Response({"detail": "Product size not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSizeSerializerwrite(
            size,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if request.method == 'DELETE':
        try:
            size = productsizes.objects.get(pk=pk)
            size.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except productsizes.DoesNotExist:
            return Response({"detail": "Product size not found"}, status=status.HTTP_404_NOT_FOUND)


#product colorwrite
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
def Product_color_insertion(request, pk=None):

    # CREATE
    if request.method == 'POST':
        serializer = ProductColorSerializerwrite(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # READ
    if request.method == 'GET':
        if pk:
            try:
                color = ProductSizeColor.objects.get(pk=pk)
                serializer = ProductColorSerializerwrite(color)
                return Response(serializer.data)
            except ProductSizeColor.DoesNotExist:
                return Response({"detail": "Product color not found"}, status=status.HTTP_404_NOT_FOUND)

        colors = ProductSizeColor.objects.all()
        serializer = ProductColorSerializerwrite(colors, many=True)
        return Response(serializer.data)

    # UPDATE
    if request.method in ['PUT', 'PATCH']:
        try:
            color = ProductSizeColor.objects.get(pk=pk)
        except ProductSizeColor.DoesNotExist:
            return Response({"detail": "Product color not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductColorSerializerwrite(
            color,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if request.method == 'DELETE':
        try:
            color = ProductSizeColor.objects.get(pk=pk)
            color.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductSizeColor.DoesNotExist:
            return Response({"detail": "Product color not found"}, status=status.HTTP_404_NOT_FOUND)


#Adminoffer
@parser_classes([MultiPartParser, FormParser])
@api_view(['GET', 'POST','PUT','DELETE','PATCH'])
def mainoffer_admin(request,pk=None):
    if request.method == 'POST':
        data=request.data.copy()
        #data['user']= request.user.id
        serializer= MainOfferSerializer(data=data)
        if serializer.is_valid():
         serializer.save()
         return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        if pk:
            try:
                mainOffer = MainOffer.objects.get(pk=pk)
                serializer = MainOfferSerializer(mainOffer)
                return Response(serializer.data)
            except MainOffer.DoesNotExist:
                return Response({"detail": "MainOffer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = MainOffer.objects.all()
            serializer = MainOfferSerializer(categories, many=True)
            return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        try:
            mainOffer = MainOffer.objects.get(pk=pk)
        except MainOffer.DoesNotExist:
            return Response({"detail": "MainOffer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = MainOfferSerializer(mainOffer, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            mainOffer = MainOffer.objects.get(pk=pk)
        except MainOffer.DoesNotExist:
            return Response({"detail": "MainOffer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        mainOffer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#admin offer
@parser_classes([MultiPartParser, FormParser])
@api_view(['GET', 'POST','PUT','DELETE','PATCH'])
def offer_admin(request,pk=None):
    if request.method == 'POST':
        data=request.data.copy()
        #data['user']= request.user.id
        serializer= OfferWriteSerializer(data=data)
        if serializer.is_valid():
         serializer.save()
         return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        if pk:
            try:
                offer = Offer.objects.get(pk=pk)
                serializer = OfferWriteSerializer(offer)
                return Response(serializer.data)
            except Offer.DoesNotExist:
                return Response({"detail": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = Offer.objects.all()
            serializer = OfferWriteSerializer(categories, many=True)
            return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({"detail": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data.copy()
        #data['user']= request.user.id
        serializer = OfferWriteSerializer(offer, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({"detail": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)