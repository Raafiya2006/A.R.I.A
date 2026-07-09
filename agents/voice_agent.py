import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from faster_whisper import WhisperModel
import sounddevice as sd
import soundfile as sf
import edge_tts
import asyncio
import pygame
import pyttsx3
import tempfile
import os
import time
import numpy as np

# Load model
model = WhisperModel("base", device="cpu", compute_type="int8")

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
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

def is_speech(audio_chunk, threshold=0.02):
    """Detect if audio chunk contains speech"""
    return np.abs(audio_chunk).mean() > threshold

def listen(duration=7, sample_rate=16000):
    print("Listening...")
    
    # Record with VAD — stop early if silence detected
    chunk_size = int(sample_rate * 0.5)  # 0.5 second chunks
    max_chunks = int(duration / 0.5)
    
    audio_chunks = []
    silence_count = 0
    speech_started = False
    
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
        for _ in range(max_chunks):
            chunk, _ = stream.read(chunk_size)
            audio_chunks.append(chunk)
            
            if is_speech(chunk):
                speech_started = True
                silence_count = 0
            elif speech_started:
                silence_count += 1
                # Stop after 1.5 seconds of silence after speech
                if silence_count >= 3:
                    break
    
    if not audio_chunks:
        return ""
    
    audio = np.concatenate(audio_chunks, axis=0)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    sf.write(temp_path, audio, sample_rate)
    
    # Transcribe with VAD filter
    segments, info = model.transcribe(
        temp_path,
        language="en",
        vad_filter=True,  # Built-in VAD — filters out non-speech
        vad_parameters=dict(
            min_silence_duration_ms=500,  # Ignore silences under 500ms
            threshold=0.5  # Speech detection sensitivity
        )
    )
    
    text = " ".join([s.text for s in segments]).strip()
    
    os.unlink(temp_path)
    
    if text:
        print(f"You said: {text}")
    
    return text