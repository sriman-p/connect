"""
ASGI config for Connect project.

Supports both HTTP and WebSocket connections.
"""

import os
from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to ensure apps are loaded
django_asgi_app = get_asgi_application()

# Import Channels components after Django initialization
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from config.routing import websocket_urlpatterns

# Configure application routing
application = ProtocolTypeRouter({
    # Handle HTTP requests
    'http': django_asgi_app,

    # Handle WebSocket connections
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
