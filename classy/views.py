from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'classy/index.html', {})

def tinder(request):
    return render(request, 'classy/tinder_prac.html', {})