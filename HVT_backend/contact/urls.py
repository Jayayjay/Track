from django.contrib import admin
from django.urls import path
from .views import contact_view, success

app_name="contact"

urlpatterns = [
    path('', contact_view, name='contact_page'),
    path('success/', success, name='success')
]
