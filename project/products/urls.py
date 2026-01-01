from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    

    # Subcategories
    path('subcategories/', views.subcategory_list, name='subcategory-list'),
    path('subcategories/<int:pk>/', views.subcategory_detail, name='subcategory-detail'),

    # Products
    path('products/', views.product_list, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),

    # Orders
    path('orders/', views.order_list, name='order-list'),
    path('orders/create/', views.order_create, name='order-create'),

    #offers
    path('offers/', views.active_offers, name='active-offer-list'),
    path('offersby_campaign/', views.offers_by_campaign, name='offer-list'),

    #CATEGORY ADMIN
    path('categoryin/', views.category_insertion,name='categoryin'),
    path('categoryin/<int:pk>/', views.category_insertion,name='categoryin'),

    #subcategory admin
    path('subcategoryin/', views.sub_category_insertion,name='subcategoryin'),
    path('subcategoryin/<int:pk>/', views.sub_category_insertion,name='subcategoryin'),

    #Products admin
    path('productin/', views.Product_insertion,name='productin'),
    path('productin/<int:pk>/', views.Product_insertion,name='productin'),

    #mainoffer admin
    path('mainofferin/', views.mainoffer_admin,name='mainofferin'),
    path('mainofferin/<int:pk>/', views.mainoffer_admin,name='mainofferin'),

    #specific offers admin
    path('offerin/', views.offer_admin,name='offerin'),
    path('offerin/<int:pk>/', views.offer_admin,name='offerin'),

]
