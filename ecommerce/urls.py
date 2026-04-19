"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from retroSneaks import views as s_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # Main pages
    path('', s_views.home, name='home'),
    path('shop/', s_views.shop, name='shop'),
    path('product/<int:shoe_id>/', s_views.product_details, name='product_details'),
    path('essentials/', s_views.essentials, name='essentials'),
    path('customize/', s_views.customize, name='customize'),
    
    # Cart and checkout
    path('cart/', s_views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', s_views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', s_views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', s_views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', s_views.order_confirmation, name='order_confirmation'),
    
    # Account
    path('account/', s_views.account, name='account'),
    path('no-account/', s_views.no_account, name='no_account'),
    
    # Authentication
    path('login/', s_views.login_view, name='login'),
    path('signup/', s_views.signup, name='signup'),
    path('logout/', s_views.logout_view, name='logout'),
    
    # API endpoints
    path('api/calculate-customization-price/', s_views.calculate_customization_price, name='calculate_customization_price'),
    path('api/get-shoe-image/', s_views.get_shoe_image, name='get_shoe_image'),
    
    # Newsletter
    path('newsletter-signup/', s_views.newsletter_signup, name='newsletter_signup'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
