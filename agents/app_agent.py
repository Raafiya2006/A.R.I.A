import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import subprocess
import webbrowser
import urllib.parse
import os
import glob

APP_PATHS = {
    "vs code": r"C:\Users\Raafiya\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode": r"C:\Users\Raafiya\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "code": r"C:\Users\Raafiya\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify": r"C:\Users\Raafiya\AppData\Roaming\Spotify\Spotify.exe",
    "discord": r"C:\Users\Raafiya\AppData\Local\Discord\Update.exe",
    "whatsapp": r"C:\Users\Raafiya\AppData\Local\WhatsApp\WhatsApp.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": r"C:\Windows\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "paint": r"C:\Windows\System32\mspaint.exe",
    "file explorer": r"C:\Windows\explorer.exe",
    "explorer": r"C:\Windows\explorer.exe",
    "task manager": r"C:\Windows\System32\Taskmgr.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
}

APP_ALIASES = {
    "notepd": "notepad",
    "clculator": "calculator",
    "calcultor": "calculator",
    "clcultors": "calculator",
    "spotfy": "spotify",
    "spotif": "spotify",
    "chorme": "chrome",
    "crome": "chrome",
    "discrod": "discord",
    "whatsap": "whatsapp",
    "vs cod": "vs code",
    "vscod": "vs code",
    "fcebook": "facebook",
    "facbook": "facebook",
    "youtub": "youtube",
    "fil manager": "file explorer",
    "file mger": "file explorer",
}

def fix_mishearing(text):
    for wrong, correct in APP_ALIASES.items():
        text = text.replace(wrong, correct)
    return text

def volume_up():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
        return "Volume increased"
    except:
        # Fallback using nircmd or keyboard simulation
        subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
            '-c', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait([char]0xAF)'],
            capture_output=True)
        return "Volume increased"

def volume_down():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
        return "Volume decreased"
    except:
        subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
            '-c', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait([char]0xAE)'],
            capture_output=True)
        return "Volume decreased"

def open_app(app_name):
    app_name = fix_mishearing(app_name.lower().strip().rstrip('.!?,'))

    for key, path in APP_PATHS.items():
        if key in app_name:
            if os.path.exists(path):
                subprocess.Popen([path])
                return f"Opening {key}"
            else:
                webbrowser.open(f"https://www.{key.replace(' ', '')}.com")
                return f"Opening {key} in browser"

    websites = {
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "twitter": "https://twitter.com",
        "linkedin": "https://linkedin.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "google": "https://google.com",
        "maps": "https://maps.google.com",
        "netflix": "https://netflix.com",
        "amazon": "https://amazon.in",
        "flipkart": "https://flipkart.com",
        "erp": "https://erp.sathyabama.ac.in",
        "lms": "https://lms.sathyabama.ac.in",
    }
    for site, url in websites.items():
        if site in app_name:
            webbrowser.open(url)
            return f"Opening {site}"

    try:
        os.startfile(app_name)
        return f"Opening {app_name}"
    except:
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(app_name)}")
        return f"Searching for {app_name} online"

def open_youtube(query=None):
    if query:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}"
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"

def google_search(query):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"Searching Google for {query}"

def handle_app_command(text):
    text = fix_mishearing(text.lower())

    # Volume
    if any(w in text for w in ["volume up", "increase volume", "louder", "turn up"]):
        return volume_up()
    if any(w in text for w in ["volume down", "decrease volume", "quieter", "turn down", "lower volume"]):
        return volume_down()
    if "mute" in text:
        subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
            '-c', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait([char]0xAD)'],
            capture_output=True)
        return "Muted"

    # YouTube
    if "youtube" in text:
        if any(w in text for w in ["play", "search", "find"]):
            for word in ["play", "search for", "find", "search"]:
                if word in text:
                    query = text.split(word)[-1].replace("youtube", "").replace("on", "").strip()
                    if query:
                        return open_youtube(query)
        return open_youtube()

    # Spotify
    if "spotify" in text:
        if any(w in text for w in ["liked", "playlist", "music", "song", "play"]):
            webbrowser.open("https://open.spotify.com/collection/tracks")
            return "Opening your liked songs on Spotify"
        path = APP_PATHS["spotify"]
        if os.path.exists(path):
            subprocess.Popen([path])
            return "Opening Spotify"
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify in browser"

    # Google search
    if "search" in text and any(w in text for w in ["google", "for", "online"]):
        for trigger in ["search for", "google for", "search"]:
            if trigger in text:
                query = text.split(trigger)[-1].replace("google", "").strip()
                if query and len(query) > 2:
                    return google_search(query)

    # Gmail
    if "gmail" in text:
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail"

    # Open/launch any app
    if any(w in text for w in ["open", "launch", "start", "run"]):
        for trigger in ["open", "launch", "start", "run"]:
            if trigger in text:
                app_name = text.split(trigger)[-1].strip()
                for filler in ["the ", "my ", "an ", "a ", "please", "can you ", "could you "]:
                    app_name = app_name.replace(filler, "")
                app_name = app_name.strip().rstrip('.!?,')
                if app_name and len(app_name) > 1:
                    return open_app(app_name)

    return None