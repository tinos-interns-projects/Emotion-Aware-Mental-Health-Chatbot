# Emotion-Aware Mental Health Chatbot  

An **AI-powered chatbot** built with **Django** that supports both text and voice interactions.  
The chatbot detects user emotions, provides empathetic responses, supports **multilingual translation**, integrates **text-to-speech (TTS)**, and manages chat history.  
Designed to provide **mental health support** and **real-time conversations**.  

---

## 🚀 Features  

### 🔑 User Authentication  
- Register, Login, Logout, Profile  

### 💬 Chat System  
- Multiple chat pages per user  
- Chat history & page management  

### 🌍 Multilingual Support  
- Auto-translation via Google Translator  

### 🎙 Voice Support  
- Upload voice recordings (WebM → MP3 conversion)  
- Speech-to-Text (Whisper Model)  
- Text-to-Speech responses (pyttsx3)  

### 🤖 AI Integration  
- Emotion-aware responses using `ask_ollama` (LLM backend)  

### 🧹 Chat Management  
- Clear chat history  
- Delete specific chat pages  
- Translate chat history  

### ⚡ Real-Time TTS  
- Threaded TTS for smooth, non-blocking speech output  

---

## 🛠 Tech Stack  
- **Backend:** Django, SQLite3 (default)  
- **AI & NLP:** Ollama, Whisper, Deep Translator  
- **Voice Processing:** Pydub, Pyttsx3  
- **Frontend:** Django Templates (HTML, CSS, JS)  
- **Authentication:** Django’s built-in user system  

---

## 📂 Project Structure  

├── Bot/

│ ├── static/voice/ # Saved voice files

│ ├── templates/ # HTML templates (chat, login, profile, etc.)

│ ├── models.py # ChatMessage model

│ ├── utils.py # ask_ollama function

│ ├── views.py # Main logic (chat, voice, translation)

│ ├── urls.py # URL routing

│ └── ...

├── manage.py

└── requirements.txt



---

## ⚙️ Installation  

### 1. Clone the Repository  
```bash
git clone https://github.com/tinos-interns-projects/emotion-aware-chatbot.git
cd emotion-aware-chatbot

```
###2. Create Virtual Environment

python -m venv venv

source venv/bin/activate   # Mac/Linux

venv\Scripts\activate      # Windows


###3.Install Dependencies

pip install -r requirements.txt

###4.Install Ollama (LLM Backend)

After installation, pull the required model (example: llama2 or custom model):



bash
---
ollama pull llama2

python manage.py migrate

python manage.py runserver


## ▶️ Usage  

1. Register/Login with your account.  
2. Start a chat session (text or voice).  
3. Send a message (auto-detects language & translates to English).  
4. Receive empathetic AI responses (with optional TTS playback).  
5. Manage multiple chat pages, clear or delete history.  
6. Use voice input to transcribe & interact with the bot.  

---

## 👨‍💻 Contributors  

- [Arjun K](https://github.com/Arju-Arjun)  
- [Noor Muhammed](https://github.com/noormuhammed4004)  





