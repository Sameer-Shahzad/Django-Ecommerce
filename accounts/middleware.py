import os
import socket
from django.http import HttpResponseForbidden

class AdminIPRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_path = os.getenv('ADMIN_URL_PATH', '')

        if admin_path and request.path.startswith(f'/{admin_path}/'):
            allowed_ips = ['127.0.0.1', '::1']
            
            try:
                docker_gateway = socket.gethostbyname('host.docker.internal')
                allowed_ips.append(docker_gateway)
            except socket.gaierror:
                pass

            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')

            is_docker_network = client_ip.startswith('192.168.') or client_ip.startswith('172.')

            if client_ip not in allowed_ips and not is_docker_network:
                return HttpResponseForbidden("Access Denied.")
        
        return self.get_response(request)