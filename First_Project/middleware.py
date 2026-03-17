from django.shortcuts import redirect
from django.urls import reverse

class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Sirf wo list jo bina login ke khul sakti hai
        public_urls = [
            reverse('sign_in'),
            reverse('registration'),
            # Agar koi aur page public rakhna hai to yahan add karein
        ]

        # 2. Admin aur Static files ko allow karein taake CSS na tute
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)

        # 3. ASLI CHECK: Agar banda login nahi hai aur public list mein bhi nahi hai
        if not request.session.get('email') and request.path not in public_urls:
            return redirect('sign_in')

        response = self.get_response(request)

        # 4. Back Button Block (Cache Clear)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response