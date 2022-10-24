from django.shortcuts import render
from vendor.models import Vendor

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

# Helper function or you can create utils.py
def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat

    elif 'lat' in request.GET:
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        request.session['lat'] = lat
        request.session['lng'] = lng

        return lng, lat
    else:
        return None


def home(request):

    if get_or_set_current_location(request) is not None:
        
        pnt = GEOSGeometry('POINT(%s %s)'% (get_or_set_current_location(request)))
        # print(pnt)
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=500))).annotate(distance=Distance('user_profile__location', pnt)).order_by('distance')
        # print(D(km=radius))
        for v in vendors:
            v.kms = round(v.distance.km, 1) # distance was taken from annotate method

    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:4] # list slicing
        # print(vendors) # will print queryset in list structure
        # for i in vendors:
        #     print(type(i.vendor_name)) # Will print string data
        #     print(i.vendor_name) # Will print the value of vendor_name field of the Vendor Table or Models

    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)