import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import subprocess
import socket
import os

def get_network_devices():
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        prefix = ".".join(local_ip.split(".")[:3])

        # Run ARP scan
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")

        devices = []
        for line in lines:
            if prefix in line:
                parts = line.split()
                for part in parts:
                    part = part.strip("()")
                    if part.startswith(prefix):
                        try:
                            name = socket.gethostbyaddr(part)[0]
                        except:
                            name = "Unknown"
                        if part != local_ip:
                            devices.append(f"{part} ({name})")
                        break

        if not devices:
            return "No other devices found on your network right now."

        response = f"Found {len(devices)} devices on your network: "
        response += ", ".join(devices[:6])
        return response

    except Exception as e:
        return f"Could not scan network: {e}"

def volume_up():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume increased to {int(new_vol * 100)}%"
    except Exception as e:
        return f"Volume error: {e}"

def volume_down():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - 0.1)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume decreased to {int(new_vol * 100)}%"
    except Exception as e:
        return f"Volume error: {e}"

def set_volume(percent):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(percent / 100, None)
        return f"Volume set to {percent}%"
    except Exception as e:
        return f"Volume error: {e}"

def mute():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
        return "Muted"
    except Exception as e:
        return f"Mute error: {e}"

def unmute():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)
        return "Unmuted"
    except Exception as e:
        return f"Unmute error: {e}"

def take_screenshot():
    try:
        from PIL import ImageGrab
        import datetime
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = f"C:\\Raafiya\\A.R.I.A\\{filename}"
        img = ImageGrab.grab()
        img.save(path)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"

def lock_screen():
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Screen locked."
    except Exception as e:
        return f"Lock error: {e}"

def shutdown():
    subprocess.run(["shutdown", "/s", "/t", "10"])
    return "Shutting down in 10 seconds."

def restart():
    subprocess.run(["shutdown", "/r", "/t", "10"])
    return "Restarting in 10 seconds."

def brightness_up():
    try:
        subprocess.run([
            'powershell', '-c',
            '(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::Min(100, (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness + 10))'
        ], capture_output=True)
        return "Brightness increased"
    except Exception as e:
        return f"Brightness error: {e}"

def brightness_down():
    try:
        subprocess.run([
            'powershell', '-c',
            '(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::Max(0, (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness - 10))'
        ], capture_output=True)
        return "Brightness decreased"
    except Exception as e:
        return f"Brightness error: {e}"