from menu.models import FoodItem
from .models import Cart, Tax



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
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            # cartitem = Cart.objects.get(id=item.id, fooditem=item.fooditem)
            # subtotal += (cartitem.fooditem.price * item.quantity)
            fooditem = FoodItem.objects.get(id=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)

        get_tax = Tax.objects.filter(is_active=True)

        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            # print(tax_amount)
            tax_dict.update({tax_type: {str(tax_percentage):tax_amount}}) # key must be string to recognize as key in dictionary
            # {'EVAT': {'12.00': '48'}}
            # {'EVAT': {'tax_type': 'tax_amount'}}

        # print(tax_dict)
        # tax = 0
        # for key in tax_dict.values():
        #     for x in key.values():
        #         tax = tax + x

        tax = sum(x for key in tax_dict.values() for x in key.values())
        grand_total = subtotal + tax
    
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)