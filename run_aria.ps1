Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& c:\Raafiya\A.R.I.A\venv\Scripts\Activate.ps1
$env:PATH += ";C:\Raafiya\A.R.I.A\ffmpeg-master-latest-win64-gpl-shared\bin"
$env:PATH += ";C:\Users\Raafiya\AppData\Local\Programs\Ollama"
$env:OLLAMA_MODELS = "E:\ollama_models"
Start-Process "C:\Users\Raafiya\AppData\Local\Programs\Ollama\ollama app.exe"
Start-Sleep -Seconds 5
python main.py
