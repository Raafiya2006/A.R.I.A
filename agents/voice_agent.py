import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import whisper
import sounddevice as sd
import soundfile as sf
import edge_tts
import asyncio
import pygame
import pyttsx3
import tempfile
import os
import time

# Load Whisper model
model = whisper.load_model("base")

# Initialize pygame for audio playback
pygame.mixer.init()

async def _speak_async(text):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name
    await communicate.save(tmp_path)
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    time.sleep(0.2)
    try:
        os.unlink(tmp_path)
    except:
        pass

def speak(text):
    print(f"ARIA: {text}")
    try:
        asyncio.run(_speak_async(text))
    except Exception:
        # Fallback to pyttsx3 if no internet
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

def listen(duration=8, sample_rate=16000):
    print("Listening...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    sf.write(temp_path, audio, sample_rate)
    result = model.transcribe(temp_path, language='en')
    os.unlink(temp_path)
    text = result['text'].strip()
    print(f"You said: {text}")
    return text