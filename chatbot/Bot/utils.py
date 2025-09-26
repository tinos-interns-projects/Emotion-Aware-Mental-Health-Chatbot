import ollama
from .models import ChatMessage

def ask_ollama(page,message: str, user, user_name: str = "User") -> str:
    """
    Respond empathetically with short, supportive messages.
    Maintain conversation context from previous messages.
    Understand any input language, but always reply in English.
    """

  
    # Fetch last 10 messages from DB (user + bot) for context
    history = list(ChatMessage.objects.filter(user=user, page=page).order_by("timestamp"))[:-2]
     # Convert to list for easier manipulation
    # Base system instruction
    messages = [
        {
            "role": "system",
            "content": (
                "You are 'EmoBot', an empathetic AI mental health assistant. "
                "⚠️ Your ONLY role is to support emotional well-being, mental health concerns, stress, anxiety, loneliness, or related feelings. "
                "❌ You must NEVER provide coding, math, factual, technical, medical, or general knowledge answers — not even after giving a redirection. "
                "If the user asks something unrelated to emotions or mental health, "
                "your reply must ONLY be this (word for word): "
                "\"I understand your curiosity, but I’m here to focus on how you’re feeling. Would you like to share what’s on your mind today?\" "
                "Do not add or explain anything else. "
                "You must understand user input in ANY language "
                "Keep replies short (1–3 sentences), caring, and supportive. "
                "Never translate the user’s text back. "
                "💡 If the user expresses extreme distress or mentions self-harm/suicidal thoughts, always reply with: "
                "\"I’m really concerned about your safety. You are not alone—please reach out to a trusted person or a local crisis helpline immediately. "
                "If you are in India, you can call Vandrevala Foundation Helpline at 1860 266 2345. "
                "If elsewhere, please look up your local emergency number or helpline.\" "
                "Stay empathetic, warm, and non-judgmental in all responses."
                "you can understand malayalam but you can't understand manglish (malayalam typed in english letters)."
                
            )
        }
    ]

    # Add past conversation
    for msg in history:
        if msg.is_bot:
            messages.append({"role": "assistant", "content": msg.message})
        else:
            messages.append({"role": "user", "content": msg.message})

    # Add the new user message
    messages.append({"role": "user", "content": message})

  

    # Send full conversation to Ollama
    response = ollama.chat(model="gemma:7b", messages=messages)

    # Return bot reply safely
    return response["message"]["content"] if "message" in response else ""
