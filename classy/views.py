from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('<p>classy there</p>')

def tinder(request):
    return render(request, 'classy/tinder_prac.html', {})