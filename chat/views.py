from django.http import Http404
from django.shortcuts import render, HttpResponse

from .models import *

def index(request):
    return HttpResponse("Index page placeholder")

def chatroom(request, slug):
    try:
        r = Chatroom.objects.get(pk=slug)
    except Chatroom.DoesNotExist:
        raise Http404("Chatroom does not exist!")
    return HttpResponse("Chatroom page placeholder")

