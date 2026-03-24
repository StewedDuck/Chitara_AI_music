from django.contrib import admin
from .models import (
    User,
    SongLibrary,
    GenerationParameters,
    Song,
    SongGenerationRequest,
    SharedLink,
    Notification
)


admin.site.register(User)
admin.site.register(SongLibrary)
admin.site.register(GenerationParameters)
admin.site.register(Song)
admin.site.register(SongGenerationRequest)
admin.site.register(SharedLink)
admin.site.register(Notification)