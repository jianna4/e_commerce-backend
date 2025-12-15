from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    SubCategoryListView, SubCategoryDetailView,
    ProductListView, ProductDetailView,
    OrderListView, OrderDetailView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/<slug:slug>/', CategoryDetailView.as_view()),

    path('subcategories/', SubCategoryListView.as_view()),
    path('subcategories/<int:pk>/', SubCategoryDetailView.as_view()),

    path('products/', ProductListView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),

    path('orders/', OrderListView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
]
