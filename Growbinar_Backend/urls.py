from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404
from rest_framework.response import Response
from django.conf.urls import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Authentication.urls')),
    path('profile/',include('profile_details.urls')),
    path('sessions/',include('Sessions.urls'))
] + static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def handle404(request, *args, **kwargs):
    return Response({"message":"Invalid url"},status=404)

handler404 = handle404
