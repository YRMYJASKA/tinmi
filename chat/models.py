from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

import string, random

# An override of the default user model of Django
class Tinmiuser(AbstractUser):
    username = models.CharField(
        max_length=64, unique=True, db_index=True, primary_key=True)
    email = models.EmailField()
    date_created = models.DateField('Date of creation', default=timezone.now)

    def __str__(self):
        return self.username

# Chatroom: holds different users and also messages
class Chatroom(models.Model):
    room_id = models.SlugField(primary_key=True, unique=True, editable=False, blank=True)
    room_title = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True)    

    # All users in the chatroom
    users = models.ManyToManyField(Tinmiuser)
    # Room owner
    room_owner = models.ForeignKey(Tinmiuser, on_delete=models.PROTECT, related_name="owneruser")
    
    # On save, generate the additional room_id slug
    def save(self, *args, **kwargs):
        while not self.room_id:
            ret = []
            ret.extend(random.sample(string.ascii_letters, 3))
            ret.extend(random.sample(string.digits, 8))
            ret.extend(random.sample(string.ascii_letters, 1))

            newslug = ''.join(ret)
            if self.__class__.objects.filter(pk=newslug).count() is 0:
                self.room_id = newslug

        super(Chatroom, self).save(*args, **kwargs)

# Message: is sent to a room
class Message(models.Model):
    # Which room does this message belong to
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    
    # Which user sent this message
    sender = models.ForeignKey(Tinmiuser, on_delete=models.PROTECT)

    # Data
    content = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True) # When the message was sent
