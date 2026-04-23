from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ All APIs go through manuscripts app
    path('api/manuscripts/', include('manuscripts.urls')),
    path('api/users/', include('users.urls')),
]