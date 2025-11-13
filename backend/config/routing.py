"""
ASGI routing for WebSocket connections.
"""

from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from messaging.consumers import ChatConsumer
from documents.consumers import DocumentCollaborationConsumer
from spreadsheets.consumers import SpreadsheetCollaborationConsumer


websocket_urlpatterns = [
    # Messaging WebSocket
    re_path(r'ws/chat/(?P<channel_id>\d+)/$', ChatConsumer.as_asgi()),

    # Document collaboration WebSocket
    re_path(r'ws/documents/(?P<document_id>\d+)/$', DocumentCollaborationConsumer.as_asgi()),

    # Spreadsheet collaboration WebSocket
    re_path(r'ws/spreadsheets/(?P<spreadsheet_id>\d+)/$', SpreadsheetCollaborationConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
