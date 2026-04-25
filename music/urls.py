from django.urls import path
from . import views

urlpatterns = [
    # Generation API
    path('api/generate/', views.generate_song, name='generate_song'),
    path('api/status/<int:song_id>/', views.check_song_status, name='check_song_status'),
    
    # New CRUD endpoints
    path('api/library/', views.get_library, name='get_library'),
    path('api/songs/<int:song_id>/rename/', views.rename_song, name='rename_song'),
    path('api/songs/<int:song_id>/delete/', views.delete_song, name='delete_song'),
    path('api/songs/<int:song_id>/share/', views.share_song, name='share_song'),
]