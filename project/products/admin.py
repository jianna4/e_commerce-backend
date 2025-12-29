

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Order, OrderItem ,SubCategory,ProductImage ,productsizes ,ProductSizeColor ,Offer,MainOffer
import nested_admin

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

class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 1

class ProductSizeColorInline(nested_admin.NestedTabularInline):
    model = ProductSizeColor
    extra = 1
    fields = ['color_name', 'hex_code', 'quantity']  # quantity is editable here!

class ProductSizeInline(nested_admin.NestedTabularInline):
    model = productsizes
    extra = 1
    inlines = [ProductSizeColorInline]

class OfferInline(nested_admin.NestedTabularInline):
    model = Offer
    extra = 1
    fields = [ 'campaign', 'new_price', 'old_price', 'percentage_off', 'is_active',]
    readonly_fields = ['old_price', 'is_active', 'percentage_off']


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'subcategory', 'created_at']
    list_filter = ['available', 'subcategory']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields =['stock','created_at', 'updated_at']
    inlines = [ProductImageInline, ProductSizeInline , OfferInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'total')  # auto-calculated, not editable
    fields = ('product', 'quantity', 'size', 'color', 'price', 'total')  # order of fields

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]

@admin.register(MainOffer)
class MainOfferAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'description', 'start_date',
        'end_date', 'is_active'
    ]

    readonly_fields = ['is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title']
