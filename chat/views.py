from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate 
from django.shortcuts import redirect, render, HttpResponse
from django.utils.safestring import mark_safe
from django.template import loader

import json
import re
from .models import *
from .forms import *

# 
def index(request):
    # If the user has already logged in
    if request.user.is_authenticated:
        return redirect("landing")
    
    signupform = TinmiuserCreationForm()
    loginform = Tinmiuser

    return render(request, 'chat/index.html', {'user': request.user, 'signupform': signupform, 'loginform': loginform,})

@login_required
def landing(request):
    return render(request, 'chat/landing.html', {'user': request.user})

@login_required
def chatroom(request, slug):
    r = None
    # Check if the requested chatroom even exists
    try:
        r = Chatroom.objects.get(pk=slug)
    except Chatroom.DoesNotExist:
        raise Http404("Chatroom does not exist!")

    # Return the rendered template 
    return render(request, 'chat/chatroom.html', {
        'room_id_json': mark_safe(json.dumps(slug)),
        'room_title': r.room_title
        })

# Sign-up view
def signup(request):
    if request.method == 'POST':
        form = TinmiuserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')

            # Remove XSS in the username
            username = re.sub(re.compile('<.*?>'), '', username)

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            next = request.POST.get('next', '/')
            return redirect(next)

    else:
        form = TinmiuserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})
# Room creation view
@login_required
def createroom(request):
    if request.method == 'POST':
        form = RoomForm(request.POST) 
        print(request.POST)
        if form.is_valid():
            if form.cleaned_data['room_title'] == "": 
                return JsonResponse({'success': False})
            theroom = Chatroom(room_title = form.cleaned_data['room_title'], room_owner = request.user)
            theroom.save()
            theroom.users.add(request.user)
            return JsonResponse({'success': True, 'room_id':theroom.room_id, 'room_title': theroom.room_title})
    else:
        return HttpResponseBadRequest("Bad Request")

# Leave the room of provided id,
# then if no more people are in the chatroom => delete it
@login_required
def leaveroom(request):
    r = None
    try:
        r = Chatroom.objects.get(room_id = request.POST.get('room_id'))
    except Chatroon.DoesNotExist:
        return JsonResponse({'success': False})

    if request.user not in r.users.all():
        return JsonResponse({'success': False})
    
    r.users.remove(request.user)
    r.save()
    response = {'success': True, 'deleted_room': False}  
    if len(r.users.all()) < 1:
        print("Room '%s' deleted. No more members" % request.POST.get("room_id"))
        r.delete()
        response['deleted_room']= True

    return JsonResponse(response)

# Return JSON boolean depending on if requested room is valid
# Meant to be used via AJAX
@login_required
def validate_room(request):
    requested_id = request.GET.get('room_id', None)
    data = {
            'is_valid': Chatroom.objects.filter(room_id__iexact=requested_id).exists(),
            'room_title': None,
            }

    if data['is_valid']:
        data['room_title'] = Chatroom.objects.get(room_id__iexact=requested_id).room_title

    print(data)
    return JsonResponse(data)
