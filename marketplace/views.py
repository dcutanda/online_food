
from unicodedata import category
from django.shortcuts import redirect, render, get_object_or_404
from marketplace.models import Cart
from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from vendor.views import opening_hours
from .context_processors import get_cart_count, get_cart_amounts

from django.db.models import Prefetch

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from datetime import date, datetime

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

    opening_hours = OpeningHour.objects.filter(vendor=vendor)

    # Check current days opening hours
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    # print(current_opening_hours)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print(current_time)
    # is_open = None
    # for i in current_opening_hours:
    #     start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
    #     end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
    #     # print(start, end)
    #     if start > current_time and end < current_time:
    #         is_open = True
    #         break # this will prevent to continue the for loop
    #     else:
    #         is_open = False
    # print(is_open)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).order_by('day', '-from_hour')
    else:
        cart_items = None
    
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
        
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
                    return JsonResponse({'status': 'Success', 'messages': 'Increased the cart quantity!', 'cart_counter': get_cart_count(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'messages': 'Added the food to the cart', 'cart_counter': get_cart_count(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
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
                    return JsonResponse({'status': 'Success','cart_counter': get_cart_count(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
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
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

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
                    return JsonResponse({'status': 'Success', 'messages': 'Item succesfully deleted', 'cart_counter': get_cart_count(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'messages': 'This item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'messages': 'Invalid Request'})

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']
       
        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
    
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
    
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)'% (longitude, latitude))
            # print(pnt)
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))).annotate(distance=Distance('user_profile__location', pnt)).order_by('distance')
            # print(D(km=radius))
            for v in vendors:
                v.kms = round(v.distance.km, 1) # distance was taken from annotate method
        
        # Basic search functionality
        # vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
        vendor_count = vendors.count()

        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
            'radius': radius,
        }
        return render(request, 'marketplace/listings.html', context)
        
    