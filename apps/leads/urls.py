from django.urls import path
from . import views

urlpatterns = [path("lead/", views.lead_form, name="lead_form")]
