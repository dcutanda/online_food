from django.shortcuts import render

# Create your views here.

def cprofile(request):
	return render(request, 'customer/cprofile.html')