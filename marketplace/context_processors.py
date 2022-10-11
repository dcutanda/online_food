from menu.models import FoodItem
from .models import Cart


def get_cart_count(request):

    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    else:
        cart_count = 0
    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            # cartitem = Cart.objects.get(id=item.id, fooditem=item.fooditem)
            # subtotal += (cartitem.fooditem.price * item.quantity)

            fooditem = FoodItem.objects.get(id=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)
            
        grand_total = subtotal + tax
    # print(subtotal)
    # print(grand_total)
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)