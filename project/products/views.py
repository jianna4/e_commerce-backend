from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Category, SubCategory, Product, Order , Offer
from .serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ProductSerializer,
    OrderSerializer,
    OfferSerializer,
    MainOfferSerializer,
)
from django.utils import timezone



# --------------------
# Categories
# --------------------
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


# --------------------
# Subcategories
# --------------------
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


# --------------------
# Products
# --------------------
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def category_insertion(request):
    data=request.data.copy()
    data['user']= request.user.id
    serializer= CategorySerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#subcategory list
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sub_category_insertion(request):
    data=request.data.copy()
    data['user']= request.user.id
    serializer= SubCategorySerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#product insertion
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Product_insertion(request):
    data=request.data.copy()
    data['user']= request.user.id
    serializer= ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)