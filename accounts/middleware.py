import os
from django.http import HttpResponseForbidden
from django.conf import settings

class AdminIPRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_path = getattr(settings, 'ADMIN_URL_PATH', None)

        if admin_path and request.path.startswith(f'/{admin_path}/'):
            allowed_ips = getattr(settings, 'ALLOWED_ADMIN_IPS', ['127.0.0.1', '::1'])
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            is_allowed = client_ip in allowed_ips
            is_internal = client_ip.startswith(('172.', '192.168.', '10.'))

            if not (is_allowed or is_internal):
                return HttpResponseForbidden(f"Access Denied. Your IP ({client_ip}) is not authorized.")
        
        return self.get_response(request)