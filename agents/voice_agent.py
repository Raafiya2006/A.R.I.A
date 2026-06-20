import whisper
import sounddevice as sd
import soundfile as sf
import pyttsx3
import numpy as np
import tempfile
import os

# Load Whisper model (tiny = fast, runs locally)
model = whisper.load_model("tiny")

# TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # speaking speed
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"ARIA: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(duration=5, sample_rate=16000):
    print("Listening...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # wait until recording is done

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    sf.write(temp_path, audio, sample_rate)

    # Transcribe with Whisper
    result = model.transcribe(temp_path)
    os.unlink(temp_path)  # delete temp file

    text = result['text'].strip()
    print(f"You said: {text}")
    return text