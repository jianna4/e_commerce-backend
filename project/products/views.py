from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Category, Product, Order, SubCategory
from .serializers import (
    CategorySerializer, 
      # IMPORT THIS
    ProductSerializer, 
    OrderSerializer,
    SubCategorySerializer
)
from .permissions import IsStaffOrReadOnly, IsOwnerOrStaff

# -------------------
# Categories
# -------------------
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer  # Simple serializer for list
    permission_classes = [IsStaffOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer  # USE CategoryDetailSerializer HERE
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = 'slug'


# -------------------
# subcategories
# -------------------
class SubCategoryListView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsStaffOrReadOnly]

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsStaffOrReadOnly]


# -------------------
# Products
# -------------------
class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]


# -------------------
# Orders
# -------------------
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrStaff]