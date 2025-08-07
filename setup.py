import os
import platform
import subprocess
import sys
import re

def run_command(command, shell=False):
    """Führt einen Shell-Befehl aus und behandelt Fehler."""
    try:
        result = subprocess.run(command, check=True, shell=shell, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen des Befehls: {e}")
        print(e.stderr)
        sys.exit(1)

def create_virtualenv():
    """Erstellt eine virtuelle Umgebung, falls nicht vorhanden."""
    if not os.path.exists("venv"):
        print("Erstelle virtuelle Umgebung...")
        run_command([sys.executable, "-m", "venv", "venv"])
    else:
        print("Virtuelle Umgebung existiert bereits.")

def activate_virtualenv():
    """Gibt den Pfad zum Aktivierungsskript der virtuellen Umgebung zurück."""
    system = platform.system()
    if system == "Windows":
        return os.path.join("venv", "Scripts", "activate.bat")
    else:  # Linux/Mac
        return os.path.join("venv", "bin", "activate")

def install_requirements():
    """Installiert Abhängigkeiten aus requirements.txt."""
    print("Installiere Abhängigkeiten...")
    pip = os.path.join("venv", "Scripts" if platform.system() == "Windows" else "bin", "pip")
    run_command([pip, "install", "-r", "requirements.txt"])

def validate_api_key(api_key):
    """Prüft, ob der API-Schlüssel nur gültige Zeichen enthält."""
    # Entferne ungültige Zeichen (z. B. Umlaute) und beschränke auf ASCII
    if api_key:
        api_key = re.sub(r'[^\x00-\x7F]', '', api_key)
        if not api_key:
            print("Warnung: API-Schlüssel enthielt ungültige Zeichen und wurde bereinigt.")
    return api_key

def create_env_file():
    """Erstellt .env-Datei mit optionalem YouTube API-Schlüssel."""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"{env_file} existiert bereits. Überschreiben? (y/n): ", end="")
        choice = input().strip().lower()
        if choice != "y":
            print("Behalte bestehende .env-Datei.")
            return

    print("Möchtest du einen YouTube API-Schlüssel hinzufügen? (y/n): ", end="")
    add_api_key = input().strip().lower()
    api_key = ""
    if add_api_key == "y":
        print("Gehe zu https://console.cloud.google.com/, erstelle ein Projekt, aktiviere die YouTube Data API v3 und erstelle einen API-Schlüssel.")
        print("Füge den API-Schlüssel hier ein (oder drücke Enter, um zu überspringen): ", end="")
        api_key = validate_api_key(input().strip())

    with open(env_file, "w", encoding="utf-8") as f:
        if api_key:
            f.write(f"YOUTUBE_API_KEY={api_key}\n")
        else:
            f.write("# YOUTUBE_API_KEY=dein-api-schlüssel-hier\n")
    print(f"{env_file} erfolgreich erstellt.")

def start_app():
    """Startet die Flask-App."""
    print("Starte Lern-Tracker...")
    python = os.path.join("venv", "Scripts" if platform.system() == "Windows" else "bin", "python")
    run_command([python, "app.py"], shell=True)

def main():
    """Hauptfunktion für das Setup."""
    print("=== Lern-Tracker Setup ===")
    create_virtualenv()
    install_requirements()
    create_env_file()
    start_app()

if __name__ == "__main__":
    main()