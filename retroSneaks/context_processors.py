from .models import Cart


def cart_processor(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()

    return {
        'cart_count': cart_count,
        'MEDIA_URL': '/static/'  # This should match your MEDIA_URL setting
    }