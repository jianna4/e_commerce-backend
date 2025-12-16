

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Order, OrderItem ,SubCategory ,ProductColor ,ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name', 'category__name']
    list_filter = ('category',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'subcategory', 'created_at']
    list_filter = ['available', 'subcategory']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductColorInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]
