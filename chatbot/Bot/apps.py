from django.apps import AppConfig
import subprocess
import socket
import time

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Bot'  # Must match your app folder name

    def ready(self):
        """Check if Ollama server is running; start it if not."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('127.0.0.1', 11434))
            sock.close()
            print("✅ Ollama server already running.")
        except ConnectionRefusedError:
            print("⚠️ Ollama not running. Starting Ollama...")
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True  # Required on Windows
            )
            # Wait a few seconds for the server to start
            time.sleep(5)
            print("✅ Ollama server started automatically.")
