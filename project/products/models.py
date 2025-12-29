from django.db import models
from django.db.models import Sum
from django.utils import timezone

# Create your models here.

from django.conf import settings

# --------------------
# Category
# --------------------

class Category(models.Model):
   name = models.CharField(max_length=100, unique=True)
   slug = models.SlugField(unique=True)

   description = models.TextField(
        default="General category description"
    )

   image = models.ImageField(upload_to="categories/",  blank=True,
        null=True)
   is_active = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)
   def __str__(self):
        return self.name
   

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.name} ({self.category.name})"



# --------------------
# Product
# --------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products",blank=True, null=True)
    stock = models.PositiveIntegerField(default=0 ,editable=False)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
     # Popularity & ranking
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
   
def update_product_stock(product):
    """
    Recalculates and updates the total stock for a product
    based on all ProductSizeColor quantities.
    """
    total = ProductSizeColor.objects.filter(
        product_size__product=product
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Only update if value changed (optional optimization)
    if product.stock != total:
        product.stock = total
        product.save(update_fields=['stock'])


#the sizes are stored ,diff sizeor a product,it has its colors,the colors have quantity
class productsizes(models.Model):
    product=models.ForeignKey(Product, related_name="sizes",on_delete=models.CASCADE)
    waist_shoe_size=models.CharField(max_length=50 ,help_text="sizes eg ehither S M L XL or 38 40 42")
    hips=models.CharField( max_length=50, blank=True, null=True)
    height=models.CharField( max_length=50, blank=True, null=True,help_text="height of shoeor trouser or  dress")
    def __str__(self):
        return f"{self.product.name} - {self.waist_shoe_size}"


#now the prduct color for each of thesizes
class ProductSizeColor(models.Model):
    product_size = models.ForeignKey(
        productsizes,
        related_name="colors",
        on_delete=models.CASCADE
    )

    color_name = models.CharField(max_length=50)   
    hex_code = models.CharField(max_length=7 , blank=True, null=True)  
    quantity = models.PositiveIntegerField(default=0)  # Stock quantity for this size-color combination

    def __str__(self):
        return f"{self.product_size.product.name} - {self.color_name} ({self.product_size.waist_shoe_size})"
    





class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(upload_to="products/gallery/")

    def __str__(self):
        return f"Image for {self.product.name}"



#offer identifications
class MainOffer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    

    @property
    def is_active(self):
        """Dynamically check if offer is active based on current time."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date


    def __str__(self):
        return self.title
    
    
class Offer(models.Model):
    campaign = models.ForeignKey(MainOffer, on_delete=models.CASCADE, related_name="offers", blank=True, null=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="offers")
   
    new_price=models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    percentage_off = models.PositiveIntegerField(default=0, editable=False)
   
    
    def save(self, *args, **kwargs):
        # Store old_price and percentage_off in the DB
        self.old_price = self.product.price
        try:
            self.percentage_off = round((self.old_price - self.new_price) / self.old_price * 100)
        except ZeroDivisionError:
            self.percentage_off = 0
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.campaign:
         return f"{self.campaign.title} - {self.product.name}"
        return  self.product.name
    

    
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def update_total_price(self):
        """Sum all order items' totals and update total_price"""
        total = sum(item.total for item in self.items.all())
        self.total_price = total
        self.save(update_fields=['total_price'])

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"



#order item
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # New optional fields
    size = models.CharField(max_length=50, blank=True, null=True, help_text="Optional size")
    color = models.CharField(max_length=50, blank=True, null=True, help_text="Optional color")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False,blank=True, null=True)  # new field

    def save(self, *args, **kwargs):
         # Set price from product if not already set
        if not self.price:
            self.price = self.product.price
        # Automatically calculate total before saving
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


#to auto update stock of products
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=ProductSizeColor)
def update_stock_on_color_save(sender, instance, **kwargs):
    product = instance.product_size.product
    update_product_stock(product)

@receiver(post_delete, sender=ProductSizeColor)
def update_stock_on_color_delete(sender, instance, **kwargs):
    product = instance.product_size.product
    update_product_stock(product)