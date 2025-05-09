from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

@login_required
def dashboard_view(request):
    return render(request, "users/dashboard.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('dashboard/', dashboard_view, name="dashboard"),
    path('', dashboard_view, name="home"),
    path('resume/', include('doc_parser.urls')),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
