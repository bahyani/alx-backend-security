from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import user_passes_test

def is_authenticated(user):
    return user.is_authenticated

# Rate-limited login view
@ratelimit(key='ip', rate='5/m', method='POST', block=True, group='login_anon')
@ratelimit(key='user', rate='10/m', method='POST', block=True, group='login_auth')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("Login successful")
        else:
            return HttpResponse("Invalid credentials", status=401)
    return HttpResponse("Method not allowed", status=405)