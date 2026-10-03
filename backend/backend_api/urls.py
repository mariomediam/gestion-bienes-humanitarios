"""
URL configuration for backend_api project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),

    # Router principal
    path('api/', include(router.urls)),

    # Authentication endpoints (custom SP-based)
    path('api/auth/', include('app_auth.urls')),

    # DRF browsable API login
    path('api-auth/', include('rest_framework.urls')),
        
    # SGBH endpoints
    path('api/sgbh/', include('app_sgbh.urls')),
]
