from django.shortcuts import render
from vendor.models import Vendor


def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:2] # list slicing
    # print(vendors) # will print queryset in list structure
    # for i in vendors:
    #     print(type(i.vendor_name)) # Will print string data
    #     print(i.vendor_name) # Will print the value of vendor_name field of the Vendor Table or Models 

    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)