import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gp_booking_system.settings')
application = get_asgi_application()
