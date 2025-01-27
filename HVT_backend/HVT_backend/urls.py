from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version='v1',
        description="API documentation for your Django app",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.homepage, name='index'),
    path('about/', views.about, name='about'),
    path('season_schedule/', views.season_schedule, name='schedule'),
    path('coaches/', views.coaches, name='coaches'),
    path('contact/', include('contact.urls')),
    path('api/athlete_records/', include('athlete_records.urls')),
    path('registeration/', views.registeration_view, name='registeration'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
     
]
