from django.contrib import admin
from django.urls import path
from .views import contact_view, success

urlpatterns = [
    path('', contact_view, name='contact'),
    path('success/', success, name='success')
]
