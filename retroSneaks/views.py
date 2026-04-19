from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import (
    AccessoryCategory, Profile, Shoe, ShoeImage, Accessory, AccessoryImage, Tag, Brand, 
    Cart, CartItem, CustomizationOption, CustomizationPrice, Order
)
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, CustomizationForm,
    CartItemForm, CheckoutForm, NewsletterForm
)

# Home Page
def home(request):
    # Get new arrivals (shoes with 'new_arrival' tag)
    new_arrivals = Shoe.objects.filter(tags__tag_type='new_arrival').distinct()[:4]
    
    # Get hot sales (shoes with 'hot_sale' tag)
    hot_sales = Shoe.objects.filter(tags__tag_type='hot_sale').distinct()[:4]
    
    # Get primary images for each shoe
    for shoe in new_arrivals:
        shoe.primary_image = shoe.images.filter(is_primary=True).first() or shoe.images.first()
    
    for shoe in hot_sales:
        shoe.primary_image = shoe.images.filter(is_primary=True).first() or shoe.images.first()
    
    context = {
        'new_arrivals': new_arrivals,
        'hot_sales': hot_sales,
    }
    
    return render(request, 'pages/home.html', context)

# Shop Page
def shop(request):
    # Get all shoes
    shoes = Shoe.objects.all()
    
    # Get all brands for filter
    brands = Brand.objects.all()
    
    # Apply filters
    brand_filter = request.GET.get('brand')
    if brand_filter:
        shoes = shoes.filter(brand__name=brand_filter)
    
    # Apply tag filter (new_arrival, hot_sale)
    tag_filter = request.GET.get('tag')
    if tag_filter:
        shoes = shoes.filter(tags__tag_type=tag_filter)
    
    # Apply search
    search_query = request.GET.get('search')
    if search_query:
        shoes = shoes.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    
    # Apply sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        shoes = shoes.order_by('price')
    elif sort_by == 'price_desc':
        shoes = shoes.order_by('-price')
    
    # Get primary images for each shoe
    for shoe in shoes:
        shoe.primary_image = shoe.images.filter(is_primary=True).first() or shoe.images.first()
    
    context = {
        'shoes': shoes,
        'brands': brands,
        'current_brand': brand_filter,
        'current_tag': tag_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'pages/shop.html', context)

# Product Details Page
def product_details(request, shoe_id=None):
    if not shoe_id:
        # Redirect to shop if no shoe_id is provided
        return redirect('shop')
    
    shoe = get_object_or_404(Shoe, id=shoe_id)
    images = shoe.images.all()
    
    # Get sizes available for this shoe model
    available_sizes = Shoe.objects.filter(name=shoe.name).values_list('size', flat=True).distinct()
    
    # Handle add to cart form
    form = CartItemForm(initial={'size': shoe.size})
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CartItemForm(request.POST)
        if form.is_valid():
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Get the selected size
            size = form.cleaned_data['size']
            
            # Get the shoe with the selected size
            size_shoe = get_object_or_404(Shoe, name=shoe.name, size=size)
            
            # Create cart item
            cart_item = CartItem(
                cart=cart,
                shoe=size_shoe,
                quantity=form.cleaned_data['quantity']
            )
            cart_item.save()
            
            messages.success(request, 'Item added to cart!')
            return redirect('cart')
    
    context = {
        'shoe': shoe,
        'images': images,
        'available_sizes': available_sizes,
        'form': form,
    }
    
    return render(request, 'pages/product_details.html', context)

# Essentials Page
def essentials(request):
    # Get all accessories
    accessories = Accessory.objects.all()
    
    # Get all categories for filter
    categories = AccessoryCategory.objects.all()
    
    # Apply category filter
    category_filter = request.GET.get('category')
    if category_filter:
        accessories = accessories.filter(category__slug=category_filter)
    
    # Apply search
    search_query = request.GET.get('search')
    if search_query:
        accessories = accessories.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    
    # Apply sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        accessories = accessories.order_by('price')
    elif sort_by == 'price_desc':
        accessories = accessories.order_by('-price')
    
    # Get primary image for each accessory
    for accessory in accessories:
        accessory.primary_image = accessory.images.first()
    
    context = {
        'accessories': accessories,
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'pages/essentials.html', context)

# Customize Page
def customize(request):
    # Get the shoe_id from the query parameter if coming from product details
    shoe_id = request.GET.get('shoe_id')
    initial_data = {}
    
    if shoe_id:
        try:
            shoe = Shoe.objects.get(id=shoe_id)
            initial_data['shoe'] = shoe
        except Shoe.DoesNotExist:
            pass
    
    # Get all available customization options
    base_colors = CustomizationPrice.objects.filter(customization_type='base_color', active=True)
    accent_colors = CustomizationPrice.objects.filter(customization_type='accent_color', active=True)
    patterns = CustomizationPrice.objects.filter(customization_type='pattern', active=True)
    
    # Default to first options if available
    if base_colors.exists() and 'base_color' not in initial_data:
        initial_data['base_color'] = base_colors.first()
    
    if accent_colors.exists() and 'accent_color' not in initial_data:
        initial_data['accent_color'] = accent_colors.first()
    
    if patterns.exists() and 'sole_pattern' not in initial_data:
        initial_data['sole_pattern'] = patterns.first()
    
    form = CustomizationForm(initial=initial_data)
    
    # Calculate initial price
    initial_price = 0
    if 'shoe' in initial_data:
        initial_price = initial_data['shoe'].price
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Store customization in session and redirect to login
            request.session['customize_data'] = request.POST
            return redirect('no_account')
        
        form = CustomizationForm(request.POST)
        if form.is_valid():
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Create cart item
            cart_item = CartItem(
                cart=cart,
                shoe=form.cleaned_data['shoe'],
                quantity=form.cleaned_data['quantity']
            )
            cart_item.save()
            
            # Add customizations to cart item
            customizations = [
                form.cleaned_data['base_color'],
                form.cleaned_data['accent_color'],
                form.cleaned_data['sole_pattern']
            ]
            
            for customization_price in customizations:
                customization_option = CustomizationOption(
                    shoe=form.cleaned_data['shoe'],
                    customization_price=customization_price
                )
                customization_option.save()
                cart_item.customizations.add(customization_option)
            
            messages.success(request, 'Customized item added to cart!')
            return redirect('cart')
    
    context = {
        'form': form,
        'base_colors': base_colors,
        'accent_colors': accent_colors,
        'patterns': patterns,
        'initial_price': initial_price,
    }
    
    return render(request, 'pages/customize.html', context)

# Cart Page
@login_required
def cart(request):
    # Get user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get cart items
    cart_items = cart.items.all()
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 50  # Fixed delivery fee
    total = subtotal + delivery_fee
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    }
    
    return render(request, 'pages/cart.html', context)


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# Update Cart Item Quantity
@login_required
@require_POST
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            
            # Recalculate cart totals
            cart = cart_item.cart
            cart_items = cart.items.all()
            subtotal = sum(item.total_price for item in cart_items)
            delivery_fee = 50  # Fixed delivery fee
            total = subtotal + delivery_fee
            
            # Return updated price information
            return JsonResponse({
                'success': True,
                'item_total': float(cart_item.total_price),
                'cart_subtotal': float(subtotal),
                'cart_total': float(total),
            })
        
        return JsonResponse({'success': False, 'error': 'Invalid quantity'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity'})
    
# Checkout
@login_required
def checkout(request):
    # Get user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get cart items
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 50  # Fixed delivery fee
    total = subtotal + delivery_fee
    
    form = CheckoutForm(initial={'shipping_address': request.user.profile.address if hasattr(request.user, 'profile') else ''})
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total
            order.save()
            
            # Add cart items to order
            for item in cart_items:
                order.items.add(item)
            
            # Clear cart items (but keep them in the database for order reference)
            cart_items.update(cart=None)
            
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'form': form,
    }
    
    return render(request, 'pages/checkout.html', context)

# Order Confirmation
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'pages/order_confirmation.html', context)


# Account Page
@login_required
def account(request):
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Handle profile update
    if request.method == 'POST':
        # Update profile information
        if 'address' in request.POST:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.address = request.POST.get('address')
            profile.phone = request.POST.get('phone')
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('account')
    
    context = {
        'orders': orders,
        'user': request.user,
    }
    
    return render(request, 'pages/account.html', context)

# No Account Page (shown when user tries to add to cart without logging in)
def no_account(request):
    return render(request, 'pages/no_account.html')

# Login Page
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to next parameter if available, otherwise to home
                next_url = request.GET.get('next', 'home')
                
                # Check if there was a pending customization
                if 'customize_data' in request.session:
                    customize_data = request.session.pop('customize_data')
                    # Redirect back to customize page with data
                    return redirect('customize')
                
                return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'pages/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# Newsletter Signup
@require_POST
def newsletter_signup(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        # In a real application, you would save this to a database
        # or integrate with an email marketing service
        email = form.cleaned_data['email']
        messages.success(request, f'Thank you for subscribing with {email}!')
    
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# AJAX endpoint to calculate customization price
def calculate_customization_price(request):
    if request.method == 'GET':
        shoe_id = request.GET.get('shoe_id')
        base_color_id = request.GET.get('base_color_id')
        accent_color_id = request.GET.get('accent_color_id')
        pattern_id = request.GET.get('pattern_id')
        quantity = int(request.GET.get('quantity', 1))
        
        # Get base price from shoe
        try:
            shoe = Shoe.objects.get(id=shoe_id)
            base_price = shoe.price
        except Shoe.DoesNotExist:
            return JsonResponse({'error': 'Invalid shoe'}, status=400)
        
        # Calculate customization price
        customization_price = 0
        
        if base_color_id:
            try:
                base_color = CustomizationPrice.objects.get(id=base_color_id)
                customization_price += base_color.price
            except CustomizationPrice.DoesNotExist:
                pass
        
        if accent_color_id:
            try:
                accent_color = CustomizationPrice.objects.get(id=accent_color_id)
                customization_price += accent_color.price
            except CustomizationPrice.DoesNotExist:
                pass
        
        if pattern_id:
            try:
                pattern = CustomizationPrice.objects.get(id=pattern_id)
                customization_price += pattern.price
            except CustomizationPrice.DoesNotExist:
                pass
        
        # Calculate total
        total_price = (base_price + customization_price) * quantity
        
        return JsonResponse({
            'base_price': float(base_price),
            'customization_price': float(customization_price),
            'total_price': float(total_price),
            'quantity': quantity
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_shoe_image(request):
    """API endpoint to get the primary image URL for a shoe"""
    if request.method == 'GET':
        shoe_id = request.GET.get('shoe_id')
        
        try:
            shoe = Shoe.objects.get(id=shoe_id)
            # Get primary image or first image
            image = shoe.images.filter(is_primary=True).first() or shoe.images.first()
            
            if image:
                return JsonResponse({
                    'success': True,
                    'image_url': image.image.url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No image found for this shoe'
                })
        except Shoe.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Shoe not found'
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    }, status=400)

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Create profile for the user
            Profile.objects.create(user=user)
            
            messages.success(request, 'Account created successfully!')
            
            # Check if there was a pending customization
            if 'customize_data' in request.session:
                customize_data = request.session.pop('customize_data')
                # Redirect back to customize page with data
                return redirect('customize')
            
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'pages/signup.html', context)
