import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import subprocess
import webbrowser
import urllib.parse

def open_youtube(query=None):
    if query:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}"
    else:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

def google_search(query):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Searching Google for {query}"

def open_spotify():
    try:
        subprocess.Popen(r"C:\Users\Raafiya\AppData\Roaming\Spotify\Spotify.exe")
        return "Opening Spotify"
    except:
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify in browser"

def open_vscode():
    try:
        subprocess.Popen(r"C:\Users\Raafiya\AppData\Local\Programs\Microsoft VS Code\Code.exe")
        return "Opening VS Code"
    except:
        return "Couldn't find VS Code"

def open_chrome():
    try:
        subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        return "Opening Chrome"
    except:
        webbrowser.open("https://google.com")
        return "Opening Chrome"

def open_whatsapp():
    try:
        subprocess.Popen(r"C:\Users\Raafiya\AppData\Local\WhatsApp\WhatsApp.exe")
        return "Opening WhatsApp"
    except:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp in browser"

def handle_app_command(text):
    text = text.lower()

    if "youtube" in text:
        # Extract search query if any
        if "play" in text or "search" in text or "find" in text:
            for word in ["play", "search for", "find", "search"]:
                if word in text:
                    query = text.split(word)[-1].strip()
                    if query and "youtube" not in query:
                        return open_youtube(query)
        return open_youtube()

    elif "google" in text and ("search" in text or "look up" in text or "find" in text):
        for word in ["search for", "look up", "find", "google", "search"]:
            if word in text:
                query = text.split(word)[-1].strip()
                if query:
                    return google_search(query)
        return google_search(text)

    elif "spotify" in text:
        return open_spotify()

    elif "vs code" in text or "vscode" in text or "code" in text:
        return open_vscode()

    elif "chrome" in text or "browser" in text:
        return open_chrome()

    elif "whatsapp" in text:
        return open_whatsapp()

    return None