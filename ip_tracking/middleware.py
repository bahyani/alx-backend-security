"""
Simple IP Tracking Middleware for Django

This middleware logs every request that comes to your Django application.
It saves: IP address, timestamp, and the URL path that was requested.
"""

from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog


class IPTrackingMiddleware(MiddlewareMixin):
    """
    This middleware runs on EVERY request to your Django app.
    It captures the visitor's IP address and saves it to the database.
    """

    def get_client_ip(self, request):
        """
        This function gets the visitor's real IP address.

        Why is this needed?
        - Sometimes your app is behind a proxy/load balancer
        - The proxy adds the real IP in a special header called 'X-Forwarded-For'
        - We check that header first, then fall back to the normal IP

        Example:
        - Direct connection: REMOTE_ADDR = '192.168.1.100'
        - Behind proxy: X-Forwarded-For = '192.168.1.100, 10.0.0.1'
                       We take the first one: '192.168.1.100'
        """
        # Step 1: Check if there's a forwarded IP (from proxy)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            # If there are multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # No proxy, just get the direct IP
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def process_request(self, request):
        """
        This function runs BEFORE your view handles the request.

        It does 3 things:
        1. Gets the visitor's IP address
        2. Gets the URL path they visited
        3. Saves this information to the database

        Example:
        If someone visits: http://yoursite.com/products/
        This will log:
        - IP: 192.168.1.100
        - Path: /products/
        - Timestamp: 2025-11-09 14:30:00
        """
        try:
            # Step 1: Get the visitor's IP address
            ip_address = self.get_client_ip(request)

            # Step 2: Get the URL path they're visiting
            path = request.path  # Example: '/products/' or '/admin/'

            # Step 3: Get the HTTP method (GET, POST, etc.)
            method = request.method  # Example: 'GET' or 'POST'

            # Step 4: Get the browser/device info (optional)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Step 5: Save everything to the database
            RequestLog.objects.create(
                ip_address=ip_address,
                path=path,
                method=method,
                user_agent=user_agent
            )

            # You can uncomment this to see logs in your console
            # print(f"✅ Logged: {ip_address} visited {path}")

        except Exception as e:
            # If something goes wrong, just print the error
            # Don't crash the website!
            print(f"❌ Error logging request: {e}")

        # IMPORTANT: Return None to let the request continue normally
        return None