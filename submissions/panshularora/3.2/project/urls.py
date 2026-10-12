from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calls/', include('calls.urls', namespace='calls')),
    path('api/v1/', include('calls.api_urls')),
]
