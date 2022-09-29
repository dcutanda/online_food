from unicodedata import category
from django.shortcuts import render, get_object_or_404
from marketplace.models import Cart
from vendor.models import Vendor
from menu.models import Category, FoodItem

from django.db.models import Prefetch

from django.http import HttpResponse, JsonResponse

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

    context = {
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # Check if food exist in marketplace
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if already added to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'messages': 'Increased the cart quantity!'})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'messages': 'Added the food to the cart'})
            except:
                return JsonResponse({'status': 'Failed', 'messages': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'messages': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'Failed', 'messages': 'Please log in to continue!'})