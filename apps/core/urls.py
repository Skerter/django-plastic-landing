from django.urls import path
from . import views

urlpatterns = [
    path('cookie-consent/', views.cookie_consent, name='cookie_consent'),
]