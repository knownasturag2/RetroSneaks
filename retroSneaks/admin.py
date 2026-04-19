from django.contrib import admin
from .models import (
    Brand, Tag, Shoe, ShoeImage, AccessoryCategory, Accessory, 
    AccessoryImage, CustomizationPrice, CustomizationOption,
    Cart, CartItem, Order, Profile
)

class ShoeImageInline(admin.TabularInline):
    model = ShoeImage
    extra = 1

class CustomizationOptionInline(admin.TabularInline):
    model = CustomizationOption
    extra = 1

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'price', 'stock', 'condition', 'created_at')
    list_filter = ('condition', 'size', 'tags')
    search_fields = ('name', 'description')
    inlines = [ShoeImageInline, CustomizationOptionInline]
    filter_horizontal = ('tags',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag_type', 'slug')
    list_filter = ('tag_type',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class AccessoryImageInline(admin.TabularInline):
    model = AccessoryImage
    extra = 1

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    inlines = [AccessoryImageInline]

@admin.register(AccessoryCategory)
class AccessoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CustomizationPrice)
class CustomizationPriceAdmin(admin.ModelAdmin):
    list_display = ('customization_type', 'color', 'pattern', 'price', 'active')
    list_filter = ('customization_type', 'active', 'color', 'pattern')
    search_fields = ('color', 'pattern')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_price', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'shipping_address')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('items',)