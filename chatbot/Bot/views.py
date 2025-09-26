from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from deep_translator import GoogleTranslator
from pydub import AudioSegment
import os
import threading
import pyttsx3
import socket

from .utils import ask_ollama
from .models import ChatMessage

# ---------------- User Authentication ----------------
def user_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = email
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        User.objects.create_user(username=username, password=password, email=email, first_name=name)
        messages.success(request, "Account created! Please log in.")
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# ---------------- Chat Page ----------------
@login_required


def chat_page(request,):
    # If the request is POST → create a new chat page
    if request.method == "POST":
        # Find the highest page number for this user
        last_page = ChatMessage.objects.filter(user=request.user).order_by("-page").first()
        if last_page:
            new_page = last_page.page + 1
        else:
            new_page = 1  # First chat for this user

       
        # Create an empty first entry for the new page (optional)
        # ChatMessage.objects.create(user=request.user, page=new_page, message="", is_bot=False)
        #flash message
        messages.success(request, f"New chat page {new_page}.")
        return redirect("chat_page_with_page", page=new_page)

    # Default → show page 1
    return redirect("chat_page_with_page", page=1)


@login_required
def chat_page_with_page(request, page):
    history = ChatMessage.objects.filter(user=request.user, page=page).order_by("timestamp")
    current_page = page
    request.session['current_page'] = current_page 
    page_list = ChatMessage.objects.filter(user=request.user).values_list('page', flat=True).distinct()
    
    if not history:
        messages.info(request, "No messages yet. Start a new conversation!")
    return render(request, "chat.html", {"history": history, "current_page": current_page, "page_list": page_list})


# ---------------- Text-to-Speech ----------------


def is_internet_available(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def text_to_audio(text):
    def speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    # Run the speak function in a separate thread
    threading.Thread(target=speak).start()



# ---------------- Bot Response (Typed Message) ----------------
@login_required
@csrf_exempt
def get_bot_response(request):
    if request.method == "POST":
        page=request.session.get('current_page', 1)  # Default to page 1 if not set
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\Current Page:", page)
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({"reply": "Please enter a message."})
       
       

        if is_internet_available():
            try:
                # Auto-detect and translate to English
                
                translated_message = GoogleTranslator(source='auto', target='en').translate(user_message)

                print("\n\nTranslated Message:", translated_message)
            except Exception as e:
                print(f"Translation error: {e}")
        else:
            translated_message = user_message
        

        # Save user message
        ChatMessage.objects.create(user=request.user, message=user_message, is_bot=False,page=page)

        # Get bot reply
    
        bot_reply = ask_ollama(page,translated_message, request.user, request.user.first_name)
      
        # Save bot reply
        ChatMessage.objects.create(user=request.user, message=bot_reply, is_bot=True , page=page)

        # Optional: TTS
        text_to_audio(bot_reply)

        return JsonResponse({"reply": bot_reply})

    return JsonResponse({"error": "Invalid request method"}, status=400)


# ---------------- Clear Chat History ----------------
@login_required
def clear_history(request):
    if request.method == "POST":
        page=request.session.get('current_page', 1)  # Default to page 1 if not set
        ChatMessage.objects.filter(user=request.user,page=page).delete()
        messages.success(request, "Chat history cleared.")
        # messages.error(request, "No messages yet. Start a new conversation!")
        return redirect('chat')
    return JsonResponse({"error": "Invalid request method"}, status=400)


# ---------------- User Profile ----------------
@login_required
def user_profile(request):
    return render(request, 'profile.html', {"user": request.user})


# ---------------- Voice Audio Upload & Recognition ----------------
@login_required
@csrf_exempt
def voice_2_text(request, mp3_path):
    print("called successfully...")
    # mp3_path=r"C:\Users\ARJUN K\Downloads\life.mp3"
    model_size = "small"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, _ = model.transcribe(mp3_path, beam_size=5,)
    text_result = " ".join([seg.text for seg in segments])
    print("waiting for returning")
    print("output",text_result)

    # Return transcription + static filepath
    return JsonResponse({
        "status": "success",
        "text": text_result,
        "filepath": f"/static/voice/{os.path.basename(mp3_path)}"
    })






def convert_webm_to_mp3(input_path, output_path):
    """
    Convert a webm audio file to mp3 format.
    """
    try:
        audio = AudioSegment.from_file(input_path, format="webm")
        audio.export(output_path, format="mp3")
        return True, output_path
    except Exception as e:
        return False, str(e)


@login_required
@csrf_exempt
def save_voice(request):
    if request.method == "POST" and request.FILES.get("voice"):
        voice_file = request.FILES["voice"]

        voice_dir = os.path.join(settings.BASE_DIR, "Bot", "static", "voice")
        os.makedirs(voice_dir, exist_ok=True)

        # Save temporary .webm
        webm_path = os.path.join(voice_dir, voice_file.name)
        with open(webm_path, "wb+") as f:
            for chunk in voice_file.chunks():
                f.write(chunk)

        # Define mp3 filename
        mp3_filename = os.path.splitext(voice_file.name)[0] + ".mp3"
        mp3_path = os.path.join(voice_dir, mp3_filename)

        # Convert webm → mp3
        success, result = convert_webm_to_mp3(webm_path, mp3_path)

        if success:
            if os.path.exists(webm_path):
                os.remove(webm_path)
        print("Loading...")
        return voice_2_text(request, mp3_path)




@login_required
def translate_chat(request):
    if is_internet_available():
        lang = request.POST.get("lang", "en")
        page = request.session.get("current_page", 1)  
        history = ChatMessage.objects.filter(user=request.user, page=page).order_by("timestamp")

        translated_history = []
        for msg in history:
            try:
                translated_text = GoogleTranslator(source="auto", target=lang).translate(msg.message)
            except Exception:
                translated_text = msg.message  

            translated_history.append({
                "message": translated_text,
                "is_bot": msg.is_bot,
                "timestamp": msg.timestamp,
            })

        return render(request, "chat.html", {
            "history": translated_history,
            "current_page": page,
            "selected_lang": lang,
        })
    else:
        messages.error(request, "Internet not available. Translation requires an active internet connection.")
        return redirect("chat_page_with_page", page=request.session.get("current_page", 1))

#delete_chat
@login_required
def delete_chat(request, page):
    if request.method == "POST":
        ChatMessage.objects.filter(user=request.user, page=page).delete()
        messages.success(request, f"Chat page {page} deleted.")
        return redirect('chat')
    return JsonResponse({"error": "Invalid request method"}, status=400)
