from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Tinmiuser, Chatroom

class TinmiuserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Tinmiuser
        fields = ('username', 'email')
    def __init__(self, *args, **kwargs):
        super(TinmiuserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "username"
        self.fields['email'].label = "email"
        self.fields['password1'].label = "password"
        self.fields['password2'].label = "password confirmation"
        self.fields['password1'].help_text = ">8 characters"
        self.fields['password2'].help_text = ""

class TinmiuserChangeForm(UserChangeForm):
    class Meta(UserCreationForm):
        model = Tinmiuser
        fields = ('username', 'email')

class RoomForm(forms.ModelForm):
    class Meta:
        model = Chatroom
        fields = ['room_title']
    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.fields['room_title'].label = "room title"
