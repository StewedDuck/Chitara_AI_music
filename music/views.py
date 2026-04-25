import json, requests, uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from .models import User, GenerationParameters, SongGenerationRequest, Song, SongLibrary, SharedLink
from .strategies.strategy_selector import get_song_generator_strategy

def home(request):
    """Renders the main dashboard for creators and landing page for guests."""
    context = {}
    if request.user.is_authenticated:
        # Fetch or create the custom Domain User instance linked to Google email
        domain_user, _ = User.objects.get_or_create(
            email=request.user.email,
            defaults={"name": request.user.username, "role": "CREATOR"}
        )
        # Get songs for this specific user, newest first
        songs = Song.objects.filter(owner=domain_user).order_by('-created_at')
        context['songs'] = songs
        context['domain_user'] = domain_user 
    return render(request, 'home.html', context)

@csrf_exempt
def generate_song(request):
    """API Endpoint to handle song generation requests."""
    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            data = json.loads(request.body)
            user = User.objects.get(email=request.user.email)
            library, _ = SongLibrary.objects.get_or_create(owner=user)
            params = GenerationParameters.objects.create(
                genre=data.get('genre', 'Pop'),
                mood=data.get('mood', 'Happy'),
                voice_type=data.get('voice_type', 'Female'),
                prompt=data.get('prompt', 'A song about software design')
            )
            generation_request = SongGenerationRequest.objects.create(
                requester=user, parameters=params, status="PENDING"
            )
            strategy = get_song_generator_strategy()
            print(f"\n>>> [STRATEGY SELECTOR] Active Strategy: {strategy.__class__.__name__}\n")
            result = strategy.generate(generation_request)
            if result.get("status") == "FAILED":
                print(f"\n! SUNO API ERROR: {result.get('error')}\n")
                generation_request.status = "FAILED"
                generation_request.save()
                return JsonResponse({"error": f"Suno API Rejected Request: {result.get('error')}"}, status=400)
            
            song_status = "GENERATED" if result.get("status") == "SUCCESS" else "DRAFT"
            final_title = result.get("title") or data.get('prompt', 'Untitled Song')[:50]
            song = Song.objects.create(
                title=final_title,
                audio_file=result.get("audioUrl", ""),
                status=song_status, owner=user, library=library, parameters=params
            )
            generation_request.result = song
            generation_request.status = "COMPLETED" if result.get("status") == "SUCCESS" else "PROCESSING"
            generation_request.task_id = result.get("taskId") or result.get("task_id")
            generation_request.save()
            return JsonResponse({"message": "Generation initiated", "request_id": generation_request.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    return JsonResponse({"error": "POST only"}, status=405)

@csrf_exempt
def check_song_status(request, song_id):
    """Polls Suno API and saves the audio link to keep the song."""
    if request.method == "GET":
        try:
            song = get_object_or_404(Song, id=song_id)
            gen_request = SongGenerationRequest.objects.filter(result=song).first()
            if not gen_request or not gen_request.task_id:
                return JsonResponse({"error": "Task ID not found"}, status=404)
            headers = {"Authorization": f"Bearer {settings.SUNO_API_KEY}"}
            url = f"https://api.sunoapi.org/api/v1/generate/record-info?taskId={gen_request.task_id}"
            response = requests.get(url, headers=headers)
            suno_data = response.json()

            if suno_data.get("code") == 200 and ("SUCCESS" in str(suno_data) or "COMPLETED" in str(suno_data)):
                data_dict = suno_data.get("data", {})
                response_dict = data_dict.get("response") or {}
                suno_songs = response_dict.get("sunoData") or []
                if len(suno_songs) > 0:
                    audio_link = suno_songs[0].get("streamAudioUrl") or suno_songs[0].get("audioUrl")
                    if audio_link:
                        song.status = "GENERATED"
                        song.audio_file = audio_link # This "keeps" the song
                        song.save()
                        return JsonResponse({"status": "SUCCESS"})
            return JsonResponse({"status": "PENDING"})
        except Exception as e:
            return JsonResponse({"error": str(e), "status": "FAILED"}, status=400)

@csrf_exempt
def get_library(request):
    """Restored: API Endpoint to fetch a user's song library."""
    if request.method == "GET":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Auth required"}, status=401)
        user = User.objects.get(email=request.user.email)
        songs = Song.objects.filter(owner=user).order_by('-created_at')
        song_list = [{"id": s.id, "title": s.title, "status": s.status} for s in songs]
        return JsonResponse({"songs": song_list}, status=200)

@csrf_exempt
def rename_song(request, song_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        song = get_object_or_404(Song, id=song_id)
        song.title = data.get("title")
        song.save()
        return JsonResponse({"message": "Renamed"}, status=200)

@csrf_exempt
def delete_song(request, song_id):
    if request.method == "DELETE":
        get_object_or_404(Song, id=song_id).delete()
        return JsonResponse({"message": "Deleted"}, status=200)

@csrf_exempt
def share_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    shared_link, _ = SharedLink.objects.get_or_create(song=song, defaults={'token': str(uuid.uuid4())})
    url = f"http://127.0.0.1:8000/music/share/{shared_link.token}/"
    return JsonResponse({"share_url": url})

def public_share_view(request, token):
    """Publicly accessible view for shared songs."""
    shared_link = get_object_or_404(SharedLink, token=token)
    return render(request, 'music/share.html', {'song': shared_link.song})