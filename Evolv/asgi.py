import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Evolv.settings')

# Initialize Django first
django_asgi_app = get_asgi_application()

import Accounts.routing  # ✅ import AFTER Django is set up

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Accounts.routing.websocket_urlpatterns
        )
    ),
})
