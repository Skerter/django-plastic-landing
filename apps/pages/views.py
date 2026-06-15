from django.shortcuts import render
from django.http import HttpResponse

from .models import Certificate


def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin/

Sitemap: https://demoplast.example/sitemap.xml"""
    return HttpResponse(content, content_type='text/plain')


def home(request):
    return render(request, 'pages/home.html', {'active': 'home'})


def dostavka(request):
    return render(request, 'pages/dostavka.html', {'active': 'dostavka'})


def o_kompanii(request):
    certificates = Certificate.objects.filter(is_active=True)
    return render(
        request,
        'pages/o_kompanii.html',
        {'active': 'o-kompanii', 'certificates': certificates},
    )


def kontakty(request):
    return render(request, 'pages/kontakty.html', {'active': 'kontakty'})


def politika(request):
    return render(request, 'pages/politika.html')


def soglasie(request):
    return render(request, 'pages/soglasie.html')
