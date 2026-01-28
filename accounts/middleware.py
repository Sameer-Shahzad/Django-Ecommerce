from django.http import HttpResponseForbidden

class AdminIPRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/uCantCMe17/'):
            allowed_ips = ['127.0.0.1', '::1'] 
            
            client_ip = request.META.get('REMOTE_ADDR')
            
            print(f"Attempting IP: {client_ip}") 
            
            if client_ip not in allowed_ips:
                return HttpResponseForbidden(f"Access Denied: IP {client_ip} not allowed.")
        
        return self.get_response(request)