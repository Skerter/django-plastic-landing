from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def cookie_consent(request):
    response = HttpResponse()
    choice = request.POST.get('choice')
    if choice in ('accepted', 'necessary', 'declined'):
        response.set_cookie(
            'cookie_consent',
            choice,
            max_age=365*24*60*60,
            samesite='Lax',
            httponly=True,
            secure=not settings.DEBUG,
        )
    return response
