from django.db import models


class UserRole(models.TextChoices):
    CREATOR = "CREATOR", "Creator"
    LISTENER = "LISTENER", "Listener"


class SongStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    GENERATED = "GENERATED", "Generated"
    SHARED = "SHARED", "Shared"


class GenerationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class NotificationType(models.TextChoices):
    INFO = "INFO", "Info"
    SUCCESS = "SUCCESS", "Success"
    ERROR = "ERROR", "Error"


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CREATOR
    )

    def __str__(self):
        return f"{self.name} ({self.email})"


class SongLibrary(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="library"
    )

    def __str__(self):
        return f"{self.owner.name}'s Library"


class GenerationParameters(models.Model):
    genre = models.CharField(max_length=50)
    mood = models.CharField(max_length=50)
    voice_type = models.CharField(max_length=50)
    prompt = models.TextField()

    def __str__(self):
        return f"{self.genre} | {self.mood} | {self.voice_type}"


class Song(models.Model):
    title = models.CharField(max_length=200)
    audio_file = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=SongStatus.choices,
        default=SongStatus.DRAFT
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="songs"
    )
    library = models.ForeignKey(
        SongLibrary,
        on_delete=models.CASCADE,
        related_name="songs"
    )
    parameters = models.ForeignKey(
        GenerationParameters,
        on_delete=models.CASCADE,
        related_name="songs"
    )

    def __str__(self):
        return self.title


class SongGenerationRequest(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="generation_requests"
    )
    parameters = models.ForeignKey(
        GenerationParameters,
        on_delete=models.CASCADE,
        related_name="generation_requests"
    )
    result = models.OneToOneField(
        Song,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_request"
    )

    def __str__(self):
        return f"Request #{self.id} - {self.status}"


class SharedLink(models.Model):
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    song = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name="shared_link"
    )

    def __str__(self):
        return f"Shared link for {self.song.title}"


class Notification(models.Model):
    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    def __str__(self):
        return f"{self.type} - {self.user.name}"