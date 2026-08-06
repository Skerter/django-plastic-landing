from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse

from .models import Certificate


def robots_txt(request):
    # The showcase is closed to indexing as a whole: it must not show up in search
    # results and compete there with the client's own site. The sitemap stays valid,
    # so going live only takes replacing one directive with `Allow: /`.
    sitemap_url = request.build_absolute_uri(
        reverse("django.contrib.sitemaps.views.sitemap")
    )
    content = f"""User-agent: *
Disallow: /

Sitemap: {sitemap_url}"""
    return HttpResponse(content, content_type="text/plain")


def home(request):
    return render(request, "pages/home.html", {"active": "home"})


def dostavka(request):
    return render(request, "pages/dostavka.html", {"active": "dostavka"})


def o_kompanii(request):
    certificates = Certificate.objects.filter(is_active=True)
    return render(
        request,
        "pages/o_kompanii.html",
        {"active": "o-kompanii", "certificates": certificates},
    )


def kontakty(request):
    return render(request, "pages/kontakty.html", {"active": "kontakty"})


def politika(request):
    return render(request, "pages/politika.html")


def soglasie(request):
    return render(request, "pages/soglasie.html")
