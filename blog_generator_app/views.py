from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
import os
import assemblyai as aai
import openai
# Create your views here.


def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            # get yt title
            title = yt_title(yt_link)
            # get transcript
            transcription = get_transcription(yt_link)
            # use OpenAI to generate the blog
            blog_content = generate_blog_from_transcription(transcription, title)
            # return blog article as a response
            return JsonResponse({'content': blog_content})
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid data sent: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# ... rest of your functions ...
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "779070043395427198e4e9b43b1bf86e"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text



def generate_blog_from_transcription(transcription, title):
    # Set your OpenAI API key here
    openai.api_key = "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"

    prompt = f"Write a comprehensive blog article based on the following YouTube video titled '{title}'. The transcription is as follows:\n\n{transcription}\n\nArticle:"

    response = openai.Completion.create(
        model="GPT-4 Turbo and GPT-4",  # Replace with the actual latest model version
        prompt=prompt,
        max_tokens=1000
    )

    generated_content = response.choices[0].text.strip()
    return generated_content

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        if password == confirm_password:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

