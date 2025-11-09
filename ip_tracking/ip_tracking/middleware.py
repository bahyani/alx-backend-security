"""
IP Tracking Middleware for Django - Task 0 & Task 1

This middleware:
1. Logs every request (IP, timestamp, path) - Task 0
2. Blocks blacklisted IPs with 403 Forbidden - Task 1
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.core.cache import cache
from django_ipgeolocation import IpGeolocation
from ip_tracking.models import RequestLog

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geolocation = IpGeolocation()

    def __call__(self, request):
        # Get client IP
        ip_address = self.get_client_ip(request)

        # Check cache for geolocation data
        cache_key = f"geolocation_{ip_address}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                # Fetch geolocation data
                response = self.geolocation.query(ip=ip_address)
                geo_data = {
                    'country': response.get('country', ''),
                    'city': response.get('city', '')
                }
                # Cache for 24 hours (24 * 60 * 60 seconds)
                cache.set(cache_key, geo_data, timeout=24 * 60 * 60)
            except Exception as e:
                # Handle API errors gracefully
                geo_data = {'country': None, 'city': None}
                print(f"Geolocation error for IP {ip_address}: {e}")

        # Log request
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            method=request.method,
            country=geo_data['country'],
            city=geo_data['city']
        )

        # Process the request
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        # Handle cases with proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class IPTrackingMiddleware(MiddlewareMixin):
    """
    Middleware that:
    - Checks if IP is blacklisted (blocks with 403 if true)
    - Logs all requests to database
    """

    def get_client_ip(self, request):
        """
        Get the real IP address of the client.
        Handles cases where app is behind a proxy/load balancer.

        Returns:
            str: Client IP address
        """
        # Check X-Forwarded-For header first (for proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            # X-Forwarded-For can have multiple IPs, take the first
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Direct connection - use REMOTE_ADDR
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def process_request(self, request):
        """
        Process incoming request.

        Flow:
        1. Extract client IP
        2. Check if IP is blacklisted
        3. If blacklisted → Return 403 Forbidden (BLOCKS REQUEST)
        4. If not blacklisted → Log request and continue

        Returns:
            HttpResponseForbidden: If IP is blocked
            None: If request should continue normally
        """
        try:
            # Step 1: Get the client's IP address
            ip_address = self.get_client_ip(request)

            # Step 2: CHECK IF IP IS BLACKLISTED (Task 1)
            if BlockedIP.is_blocked(ip_address):
                # IP is blocked! Return 403 Forbidden
                # This stops the request immediately
                return HttpResponseForbidden(
                    """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>403 Forbidden</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                text-align: center;
                                padding: 50px;
                                background-color: #f5f5f5;
                            }
                            .error-box {
                                background: white;
                                padding: 30px;
                                border-radius: 10px;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                max-width: 500px;
                                margin: 0 auto;
                            }
                            h1 { color: #d32f2f; }
                            p { color: #666; }
                        </style>
                    </head>
                    <body>
                        <div class="error-box">
                            <h1>🚫 403 Forbidden</h1>
                            <p>Your IP address has been blocked from accessing this site.</p>
                            <p>If you believe this is an error, please contact the site administrator.</p>
                        </div>
                    </body>
                    </html>
                    """
                )

            # Step 3: IP is NOT blocked - Log the request (Task 0)
            path = request.path
            method = request.method
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Save to database
            RequestLog.objects.create(
                ip_address=ip_address,
                path=path,
                method=method,
                user_agent=user_agent
            )

            # Optional: Print to console for debugging
            # print(f"✅ Logged: {ip_address} visited {path}")

        except Exception as e:
            # If something goes wrong, log the error but don't crash
            print(f"❌ Error in IPTrackingMiddleware: {e}")

        # Return None to let the request continue normally
        return None