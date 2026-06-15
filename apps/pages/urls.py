from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dostavka/', views.dostavka, name='dostavka'),
    path('o-kompanii/', views.o_kompanii, name='o_kompanii'),
    path('kontakty/', views.kontakty, name='kontakty'),
    path('politika-konfidencialnosti/', views.politika, name='politika'),
    path('soglasie-na-obrabotku-pdn/', views.soglasie, name='soglasie'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
