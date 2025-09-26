from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat'),  # Root URL shows chat page (redirects to page 1 or creates new one)
    path('chat/<int:page>/', views.chat_page_with_page, name='chat_page_with_page'),

    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('get-response/', views.get_bot_response, name='get_bot_response'),
    path("text-to-audio/", views.text_to_audio, name="text_to_audio"),
    path('clear-history/', views.clear_history, name='clear_history'),
    path('profile/', views.user_profile, name='profile'),
    path("voice_2_text/", views.voice_2_text, name="voice_2_text"),
    path("save-voice/", views.save_voice, name="save_voice"),
    path("translate-chat/", views.translate_chat, name="translate_chat"),
    path("delete_chat/<int:page>/", views.delete_chat, name="delete_chat"),  # New URL pattern for deleting chat page
]
