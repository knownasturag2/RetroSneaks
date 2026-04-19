from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.contrib.auth.admin import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phone')
    search_fields = ('user__username', 'user__email', 'address', 'phone')

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    TYPE_CHOICES = (
        ('new_arrival', 'New Arrival'),
        ('hot_sale', 'Hot Sale'),
    )
    tag_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class Shoe(models.Model):
    CONDITION_CHOICES = (
        ('new', 'Brand New'),
        ('like_new', 'Like New'),
        ('used', 'Used - Good'),
        ('worn', 'Used - Worn'),
    )
    SIZE_CHOICES = [(str(size), str(size)) for size in range(39, 46)]

    name = models.CharField(max_length=200)
    description = models.TextField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Size: {self.size})"


class ShoeImage(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shoe_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.shoe.name}"


class AccessoryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Accessory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(AccessoryCategory, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AccessoryImage(models.Model):
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='accessory_images/')

    def __str__(self):
        return f"Image for {self.accessory.name}"


class CustomizationPrice(models.Model):
    CUSTOMIZATION_TYPE_CHOICES = (
        ('base_color', 'Base Color'),
        ('accent_color', 'Accent Color'),
        ('sole_color', 'Sole Color'),
        ('lace_color', 'Lace Color'),
        ('pattern', 'Pattern'),
    )
    COLOR_CHOICES = (
        ('black', 'Black'),
        ('white', 'White'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('gray', 'Gray'),
        ('multi', 'Multi-color'),
    )
    PATTERN_CHOICES = (
        ('solid', 'Solid'),
        ('striped', 'Striped'),
        ('polka', 'Polka Dot'),
        ('camo', 'Camouflage'),
        ('geometric', 'Geometric'),
        ('gradient', 'Gradient'),
    )

    customization_type = models.CharField(max_length=20, choices=CUSTOMIZATION_TYPE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)
    pattern = models.CharField(max_length=20, choices=PATTERN_CHOICES, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customization_type', 'color', 'pattern')

    def __str__(self):
        if self.customization_type == 'pattern':
            return f"{self.get_customization_type_display()}: {self.get_pattern_display()} (+${self.price})"
        return f"{self.get_customization_type_display()}: {self.get_color_display()} (+${self.price})"


class CustomizationOption(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='customization_options')
    customization_price = models.ForeignKey(CustomizationPrice, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shoe.name} - {self.customization_price}"

    @property
    def price_adjustment(self):
        return self.customization_price.price


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, null=True, blank=True)
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, null=True, blank=True)
    customizations = models.ManyToManyField(CustomizationOption, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def product(self):
        return self.shoe or self.accessory

    @property
    def base_price(self):
        return self.product.price

    @property
    def customization_price(self):
        return sum(option.customization_price.price for option in self.customizations.all())

    @property
    def customization_details(self):
        return [
            {
                'type': option.customization_price.get_customization_type_display(),
                'color': option.customization_price.get_color_display() if option.customization_price.color else None,
                'pattern': option.customization_price.get_pattern_display() if option.customization_price.pattern else None,
                'price': float(option.customization_price.price)
            }
            for option in self.customizations.all()
        ]

    @property
    def total_price(self):
        return (self.base_price + self.customization_price) * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product} in cart"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')