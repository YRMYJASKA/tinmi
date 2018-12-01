from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

admin.site.register(models.Tinmiuser, UserAdmin)

class MessagesInline(admin.TabularInline):
    model = models.Message 
    readonly_fields = ('sender', 'content', 'date')

class ChatroomAdmin(admin.ModelAdmin):
    list_display = ['room_title', 'room_id', ]
    readonly_fields = ('room_title', 'room_id', 'date')

    inlines = [MessagesInline]

admin.site.register(models.Chatroom, ChatroomAdmin)
