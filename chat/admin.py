from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models
from .forms import TinmiuserChangeForm, TinmiuserCreationForm 

class TinmiuserAdmin(UserAdmin):
    add_form = TinmiuserCreationForm
    form = TinmiuserChangeForm
    model = models.Tinmiuser
    list_display = ['username', 'email',]

class ChatroomAdmin(admin.ModelAdmin):
    list_display = ['room_title', 'room_id', ]
    readonly_fields = ('room_title', 'room_id', 'date')

admin.site.register(models.Chatroom, ChatroomAdmin)
admin.site.register(models.Tinmiuser, TinmiuserAdmin)
