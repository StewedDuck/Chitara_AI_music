import json,requests,uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from music.models import User, GenerationParameters, SongGenerationRequest,Song, SongLibrary, SharedLink
from music.strategies.strategy_selector import get_song_generator_strategy
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect

def home(request):
    """Renders the main dashboard for creators and landing page for guests."""
    context = {}
    
    if request.user.is_authenticated:
        # Fetch or create the custom User instance
        domain_user, _ = User.objects.get_or_create(
            email=request.user.email,
            defaults={"name": request.user.username, "role": "CREATOR"}
        )
        
        # Get songs for this specific user
        songs = Song.objects.filter(owner=domain_user).order_by('-created_at')
        context['songs'] = songs
        context['domain_user'] = domain_user 
        
    return render(request, 'home.html', context)

@csrf_exempt
def generate_song(request):
    """
    API Endpoint to handle song generation requests.
    """
    if request.method == "POST":
        try:
            # Parse incoming JSON data
            data = json.loads(request.body)
            
            # Require authentication
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
                
            user, _ = User.objects.get_or_create(
                email=request.user.email, 
                defaults={"name": request.user.username, "role": "CREATOR"}
            )
            
            # Ensure library created
            library, _ = SongLibrary.objects.get_or_create(owner=user)
            
            # Save the parameters
            params = GenerationParameters.objects.create(
                genre=data.get('genre', 'Pop'),
                mood=data.get('mood', 'Happy'),
                voice_type=data.get('voice_type', 'Female'),
                prompt=data.get('prompt', 'A song about software design')
            )
            
            # Create the generation request
            generation_request = SongGenerationRequest.objects.create(
                requester=user,
                parameters=params,
                status="PENDING"
            )
            
            # Get the correct strategy
            strategy = get_song_generator_strategy()
            result = strategy.generate(generation_request)
            
            if result.get("status") == "FAILED":
                generation_request.status = "FAILED"
                generation_request.save()
                return JsonResponse({"error": f"Suno API Rejected Request: {result.get('error')}"}, status=400)
            
            #Create the actual Song record so it appears in the library
            # We use the prompt as a temporary title
            song_title = data.get('prompt', 'Untitled Song')[:50] 
            
            # If the mock strategy is used, it returns SUCCESS immediately. 
            # Suno will return PENDING.
            song_status = "GENERATED" if result.get("status") == "SUCCESS" else "DRAFT"
            
            song = Song.objects.create(
                title=song_title,
                audio_file=result.get("audioUrl", ""),
                duration_seconds=180,
                status=song_status,
                owner=user,
                library=library,
                parameters=params
            )
            
            # Link the request to the new song
            generation_request.result = song
            generation_request.status = "COMPLETED" if result.get("status") == "SUCCESS" else "PROCESSING"
            generation_request.task_id = result.get("taskId") or result.get("task_id") or result.get("id") or result.get("data")
            generation_request.save()
            
            # Return the result to the client
            return JsonResponse({
                "message": "Generation initiated successfully",
                "request_id": generation_request.id,
                "strategy_used": strategy.__class__.__name__,
                "result": result
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def check_song_status(request, song_id):
    """Polls Suno API for completion status and saves the audio link."""
    if request.method == "GET":
        try:
            # 1. Get the song from the database
            song = get_object_or_404(Song, id=song_id)
            
            # 2. Find the generation request linked to this song
            gen_request = SongGenerationRequest.objects.filter(result=song).first()
            if not gen_request or not gen_request.task_id:
                return JsonResponse({"error": "Task ID not found"}, status=404)
            
            # 3. Ask Suno for the status
            headers = {"Authorization": f"Bearer {settings.SUNO_API_KEY}"}
            url = f"https://api.sunoapi.org/api/v1/generate/record-info?taskId={gen_request.task_id}"
            response = requests.get(url, headers=headers)
            suno_data = response.json()

            print("SUNO API RESPONSE:", suno_data)
            
            # 4. FIXED: Properly parse the nested JSON to save the audio link
            if suno_data.get("code") == 200 and "SUCCESS" in str(suno_data):
                data_dict = suno_data.get("data", {})
                response_dict = data_dict.get("response") or {}
                suno_songs = response_dict.get("sunoData") or []
                
                if len(suno_songs) > 0:
                    # Grab the streamAudioUrl from the first generated version
                    audio_link = suno_songs[0].get("streamAudioUrl") or suno_songs[0].get("audioUrl")
                    
                    if audio_link:
                        song.status = "GENERATED"
                        song.audio_file = audio_link # This saves the link so the song is "kept"
                        song.save()
                        return JsonResponse({"status": "SUCCESS"})
                
            return JsonResponse({"status": "PENDING"})

        except Exception as e:
            return JsonResponse({"error": str(e), "status": "FAILED"}, status=400)
        
user = User.objects.filter(email="test@example.com").first()
@csrf_exempt
def get_library(request):
    """API Endpoint to fetch a user's song library."""
    if request.method == "GET":
        # Mock user
        user = User.objects.filter(email="test@example.com").first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
            
        # Ensure library exists
        library, _ = SongLibrary.objects.get_or_create(owner=user)
        
        # Get newest songs first as per requirements
        songs = Song.objects.filter(library=library).order_by('-created_at')
        
        song_list = [{
            "id": song.id,
            "title": song.title,
            "status": song.status,
            "duration": song.duration_seconds,
            "created_at": song.created_at
        } for song in songs]
        
        return JsonResponse({"library_id": library.id, "songs": song_list}, status=200)
    return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

@csrf_exempt
def rename_song(request, song_id):
    """API Endpoint to rename a song."""
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            new_title = data.get("title")
            
            song = get_object_or_404(Song, id=song_id)
            song.title = new_title
            song.save()
            
            return JsonResponse({"message": "Song renamed successfully", "new_title": song.title}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only PUT requests are allowed"}, status=405)

@csrf_exempt
def delete_song(request, song_id):
    """API Endpoint to delete a song."""
    if request.method == "DELETE":
        song = get_object_or_404(Song, id=song_id)
        song.delete()
        return JsonResponse({"message": "Song deleted successfully"}, status=200)
    return JsonResponse({"error": "Only DELETE requests are allowed"}, status=405)

@csrf_exempt
def share_song(request, song_id):
    """API Endpoint to generate or retrieve a shared link."""
    if request.method == "GET":
        song = get_object_or_404(Song, id=song_id)
        
        # Each song has exactly one shared link
        shared_link, created = SharedLink.objects.get_or_create(
            song=song,
            defaults={'token': str(uuid.uuid4())}
        )
        
        url = f"http://127.0.0.1:8000/music/share/{shared_link.token}/"
        return JsonResponse({"share_url": url, "token": shared_link.token}, status=200)
    return JsonResponse({"error": "Only GET requests are allowed"}, status=405)