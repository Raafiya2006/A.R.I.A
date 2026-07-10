import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import (Qt, QTimer, QThread, pyqtSignal, QObject,
    QPropertyAnimation, QEasingCurve, QRect, pyqtProperty)
from PyQt6.QtGui import (QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPainterPath, QFontDatabase)
import math
import random

# ── SIGNALS ──────────────────────────────────────────────────────────────────
class ARIASignals(QObject):
    set_status = pyqtSignal(str)        # LISTENING / THINKING / SPEAKING / ONLINE
    set_transcription = pyqtSignal(str) # what you said
    set_response = pyqtSignal(str)      # what ARIA said
    set_speaking = pyqtSignal(bool)     # animate waveform

signals = ARIASignals()

# ── WAVEFORM WIDGET ───────────────────────────────────────────────────────────
class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.bars = 40
        self.heights = [2] * self.bars
        self.target_heights = [2] * self.bars
        self.is_active = False
        self.phase = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(50)

    def set_active(self, active):
        self.is_active = active

    def update_wave(self):
        self.phase += 0.3
        if self.is_active:
            for i in range(self.bars):
                wave = math.sin(self.phase + i * 0.4) * 20
                noise = random.uniform(-10, 10)
                self.target_heights[i] = max(4, 30 + wave + noise)
        else:
            for i in range(self.bars):
                wave = math.sin(self.phase * 0.3 + i * 0.5) * 3
                self.target_heights[i] = max(2, 5 + wave)

        for i in range(self.bars):
            diff = self.target_heights[i] - self.heights[i]
            self.heights[i] += diff * 0.3

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_width = w / self.bars
        center_y = h / 2

        for i in range(self.bars):
            x = i * bar_width + bar_width * 0.2
            bw = bar_width * 0.6
            bh = self.heights[i]

            # Color gradient based on position
            t = i / self.bars
            if self.is_active:
                r = int(0 + t * 0)
                g = int(180 + t * 75)
                b = int(255 - t * 55)
                alpha = 220
            else:
                r, g, b, alpha = 0, 100, 180, 120

            color = QColor(r, g, b, alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            rect_x = int(x)
            rect_w = max(2, int(bw))
            rect_h = max(2, int(bh))
            rect_y = int(center_y - rect_h / 2)
            painter.drawRoundedRect(rect_x, rect_y, rect_w, rect_h, 2, 2)

        painter.end()

# ── CIRCULAR PULSE WIDGET ─────────────────────────────────────────────────────
class PulseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.pulse_radius = 60
        self.pulse_alpha = 255
        self.pulse_growing = True
        self.is_speaking = False
        self.rotation = 0
        self.dots = 12

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_speaking(self, speaking):
        self.is_speaking = speaking

    def animate(self):
        self.rotation = (self.rotation + 2) % 360

        if self.is_speaking:
            if self.pulse_growing:
                self.pulse_radius += 1.5
                self.pulse_alpha = max(0, self.pulse_alpha - 8)
                if self.pulse_radius >= 90:
                    self.pulse_growing = False
                    self.pulse_radius = 60
                    self.pulse_alpha = 255
        else:
            self.pulse_radius = 60
            self.pulse_alpha = 255

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2

        # Outer glow ring
        for radius in [85, 80, 75]:
            alpha = max(0, 30 - (85 - radius) * 5)
            glow = QColor(0, 180, 255, alpha)
            painter.setPen(QPen(glow, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Pulse circle
        if self.is_speaking:
            pulse_color = QColor(0, 212, 255, max(0, self.pulse_alpha))
            painter.setPen(QPen(pulse_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            r = int(self.pulse_radius)
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Main circle
        gradient = QRadialGradient(cx, cy, 60)
        gradient.setColorAt(0, QColor(0, 40, 80, 200))
        gradient.setColorAt(0.7, QColor(0, 20, 50, 220))
        gradient.setColorAt(1, QColor(0, 180, 255, 255))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 180, 255, 255), 2))
        painter.drawEllipse(cx - 60, cy - 60, 120, 120)

        # Rotating dots
        for i in range(self.dots):
            angle = math.radians(self.rotation + i * (360 / self.dots))
            dot_r = 70
            dx = cx + dot_r * math.cos(angle)
            dy = cy + dot_r * math.sin(angle)
            size = 4 if i % 3 == 0 else 2
            alpha = 255 if i % 3 == 0 else 150
            dot_color = QColor(0, 212, 255, alpha)
            painter.setBrush(QBrush(dot_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(dx - size/2), int(dy - size/2), size, size)

        # ARIA text in center
        painter.setPen(QPen(QColor(0, 212, 255, 255)))
        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.drawText(QRect(cx - 40, cy - 12, 80, 24),
                        Qt.AlignmentFlag.AlignCenter, "ARIA")

        painter.end()

# ── STATUS INDICATOR ──────────────────────────────────────────────────────────
class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.status = "ONLINE"
        self.blink = True
        self.blink_state = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_blink)
        self.timer.start(500)

    def set_status(self, status):
        self.status = status
        self.update()

    def toggle_blink(self):
        self.blink_state = not self.blink_state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "ONLINE": QColor(0, 255, 128),
            "LISTENING": QColor(0, 212, 255),
            "THINKING": QColor(255, 165, 0),
            "SPEAKING": QColor(0, 255, 128),
            "OFFLINE": QColor(255, 50, 50),
        }

        color = colors.get(self.status, QColor(0, 212, 255))

        # Blinking dot
        if self.blink_state or self.status == "ONLINE":
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(10, 8, 12, 12)

            # Glow
            glow = QColor(color.red(), color.green(), color.blue(), 60)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(6, 4, 20, 20)

        # Status text
        painter.setPen(QPen(color))
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(35, 20, self.status)

        painter.end()

# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class ARIAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.R.I.A")
        self.setFixedSize(700, 600)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None

        # Central widget
        central = QWidget()
        central.setObjectName("central")
        central.setStyleSheet("""
            QWidget#central {
                background-color: rgba(5, 10, 20, 240);
                border: 1px solid rgba(0, 180, 255, 80);
                border-radius: 20px;
            }
        """)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # ── Top bar ──
        top_bar = QHBoxLayout()

        # Logo text
        logo = QLabel("A.R.I.A")
        logo.setFont(QFont("Consolas", 22, QFont.Weight.Bold))
        logo.setStyleSheet("color: #00d4ff; letter-spacing: 6px;")

        # Close button
        close_btn = QLabel("✕")
        close_btn.setFont(QFont("Consolas", 14))
        close_btn.setStyleSheet("color: rgba(0,180,255,150); padding: 5px;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda e: self.close()

        # Minimize button
        min_btn = QLabel("─")
        min_btn.setFont(QFont("Consolas", 14))
        min_btn.setStyleSheet("color: rgba(0,180,255,150); padding: 5px;")
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        min_btn.mousePressEvent = lambda e: self.showMinimized()

        top_bar.addWidget(logo)
        top_bar.addStretch()
        top_bar.addWidget(min_btn)
        top_bar.addWidget(close_btn)
        layout.addLayout(top_bar)

        # Subtitle
        subtitle = QLabel("Agentic Reasoning and Intelligence Assistant")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet("color: rgba(0,150,200,150); letter-spacing: 2px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background: rgba(0,180,255,40); max-height: 1px;")
        layout.addWidget(div)

        # ── Pulse + Status ──
        center_row = QHBoxLayout()
        center_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pulse = PulseWidget()

        # Right side info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        self.status_widget = StatusWidget()

        # System info labels
        self.sys_labels = []
        sys_info = [
            ("MODEL", "Phi-3 Mini • Ollama"),
            ("STT", "Whisper Base • Local"),
            ("TTS", "Edge TTS • GuyNeural"),
            ("MEMORY", "ChromaDB • Active"),
            ("MONITOR", "Proactive • Running"),
        ]
        for key, val in sys_info:
            row = QHBoxLayout()
            k = QLabel(f"{key}:")
            k.setFont(QFont("Consolas", 8))
            k.setStyleSheet("color: rgba(0,180,255,120);")
            k.setFixedWidth(70)
            v = QLabel(val)
            v.setFont(QFont("Consolas", 8))
            v.setStyleSheet("color: rgba(0,212,255,200);")
            row.addWidget(k)
            row.addWidget(v)
            info_layout.addLayout(row)

        info_layout.insertWidget(0, self.status_widget)
        info_layout.addStretch()

        center_row.addWidget(self.pulse)
        center_row.addSpacing(30)
        center_row.addLayout(info_layout)
        layout.addLayout(center_row)

        # ── Waveform ──
        wave_label = QLabel("AUDIO INPUT")
        wave_label.setFont(QFont("Consolas", 7))
        wave_label.setStyleSheet("color: rgba(0,150,200,100); letter-spacing: 3px;")
        wave_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(wave_label)

        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)

        # ── Transcription ──
        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet("background: rgba(0,180,255,30); max-height: 1px;")
        layout.addWidget(div2)

        you_label = QLabel("YOU")
        you_label.setFont(QFont("Consolas", 7))
        you_label.setStyleSheet("color: rgba(0,150,200,100); letter-spacing: 3px;")
        layout.addWidget(you_label)

        self.transcription = QLabel("Say something...")
        self.transcription.setFont(QFont("Consolas", 11))
        self.transcription.setStyleSheet("color: rgba(255,255,255,180); padding: 5px 0;")
        self.transcription.setWordWrap(True)
        self.transcription.setMinimumHeight(30)
        layout.addWidget(self.transcription)

        # ── ARIA Response ──
        aria_label = QLabel("ARIA")
        aria_label.setFont(QFont("Consolas", 7))
        aria_label.setStyleSheet("color: rgba(0,150,200,100); letter-spacing: 3px;")
        layout.addWidget(aria_label)

        self.response = QLabel("ARIA online. How can I help?")
        self.response.setFont(QFont("Consolas", 11))
        self.response.setStyleSheet("color: #00d4ff; padding: 5px 0;")
        self.response.setWordWrap(True)
        self.response.setMinimumHeight(40)
        layout.addWidget(self.response)

        # ── Bottom bar ──
        div3 = QFrame()
        div3.setFrameShape(QFrame.Shape.HLine)
        div3.setStyleSheet("background: rgba(0,180,255,30); max-height: 1px;")
        layout.addWidget(div3)

        bottom = QHBoxLayout()
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Consolas", 8))
        self.time_label.setStyleSheet("color: rgba(0,150,200,120);")

        version = QLabel("v1.0.0 • Sathyabama Institute")
        version.setFont(QFont("Consolas", 8))
        version.setStyleSheet("color: rgba(0,150,200,80);")

        bottom.addWidget(self.time_label)
        bottom.addStretch()
        bottom.addWidget(version)
        layout.addLayout(bottom)

        # Clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

        # Connect signals
        signals.set_status.connect(self.on_status)
        signals.set_transcription.connect(self.transcription.setText)
        signals.set_response.connect(self.response.setText)
        signals.set_speaking.connect(self.on_speaking)

        # Position bottom right
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 730, screen.height() - 660)

    def update_clock(self):
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%A %d %b %Y  •  %I:%M:%S %p"))

    def on_status(self, status):
        self.status_widget.set_status(status)
        if status == "LISTENING":
            self.waveform.set_active(True)
        elif status == "SPEAKING":
            self.waveform.set_active(True)
            self.pulse.set_speaking(True)
        else:
            self.waveform.set_active(False)
            self.pulse.set_speaking(False)

    def on_speaking(self, speaking):
        self.pulse.set_speaking(speaking)
        self.waveform.set_active(speaking)

    def paintEvent(self, event):
        # Outer glow border
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(3):
            alpha = 20 - i * 6
            glow = QColor(0, 180, 255, alpha)
            painter.setPen(QPen(glow, (3-i)*2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(i, i, self.width()-i*2, self.height()-i*2, 20, 20)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

# ── PUBLIC API ────────────────────────────────────────────────────────────────
def update_status(status):
    signals.set_status.emit(status)

def update_transcription(text):
    signals.set_transcription.emit(text)

def update_response(text):
    signals.set_response.emit(text)

def set_speaking(speaking):
    signals.set_speaking.emit(speaking)

def launch_ui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ARIAWindow()
    window.show()
    app.exec()