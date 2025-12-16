from django.urls import path
from . import views

urlpatterns = [
    # --------------------
    # Categories
    # --------------------
    path('categories/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    

    # --------------------
    # Subcategories
    # --------------------
    path('subcategories/', views.subcategory_list, name='subcategory-list'),
    path('subcategories/<int:pk>/', views.subcategory_detail, name='subcategory-detail'),

    # --------------------
    # Products
    # --------------------
    path('products/', views.product_list, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),

    # --------------------
    # Orders
    # --------------------
    path('orders/', views.order_list, name='order-list'),
    path('orders/create/', views.order_create, name='order-create'),
]
