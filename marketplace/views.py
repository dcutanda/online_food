from unicodedata import category
from django.shortcuts import render, get_object_or_404
from marketplace.models import Cart
from vendor.models import Vendor
from menu.models import Category, FoodItem
from .context_processors import get_cart_count

from django.db.models import Prefetch

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    
   
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if food exist in marketplace
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if already added to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'messages': 'Increased the cart quantity!', 'cart_counter': get_cart_count(request), 'qty': chkCart.quantity})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'messages': 'Added the food to the cart', 'cart_counter': get_cart_count(request), 'qty': chkCart.quantity})
            except:
                return JsonResponse({'status': 'Failed', 'messages': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'messages': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'messages': 'Please log in to continue!'})

def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if food exist in marketplace
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if this fooditem already added to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success','cart_counter': get_cart_count(request), 'qty': chkCart.quantity})
                except:
                    
                    return JsonResponse({'status': 'Failed', 'messages': 'There is no food was added on your cart'})
            except:
                return JsonResponse({'status': 'Failed', 'messages': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'messages': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'messages': 'Please log in to continue!'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # Check if item exists
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'messages': 'Item succesfully deleted', 'cart_counter': get_cart_count(request)})
            except:
                return JsonResponse({'status': 'Failed', 'messages': 'This item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'messages': 'Invalid Request'})