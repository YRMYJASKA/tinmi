from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
        url(r'^ws/chat/(?P<slug>[^/]+)/$', consumers.ChatConsumer),
        url(r'^wss/chat/(?P<slug>[^/]+)/$', consumers.ChatConsumer),
    ]
