from django.db import models

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
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True,
                            help_text="Enter size range, e.g., S-XL or 38-44")
     # Popularity & ranking
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="colors",
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)   # e.g. Red
    hex_code = models.CharField(max_length=7)  # e.g. #FF0000

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(upload_to="products/gallery/")

    def __str__(self):
        return f"Image for {self.product.name}"

# --------------------
# Order
# --------------------
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



# --------------------
# OrderItem
# --------------------
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
