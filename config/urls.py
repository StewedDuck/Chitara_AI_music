from django.contrib import admin
from django.urls import path, include
from music import views as music_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('music/', include('music.urls')),
    path('accounts/', include('allauth.urls')),
    path('', music_views.home, name='home'),
]
