from PyQt5.QtWidgets import QWidget, QPushButton, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

class ControlWindow(QWidget):
    """A window with controls for the simulation."""
    # Signals
    pause_toggled = pyqtSignal()
    fps_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controls")
        self.layout = QVBoxLayout()

        # Pause/Restart Button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.layout.addWidget(self.pause_button)

        # FPS Slider
        self.fps_label = QLabel("FPS: 60")
        self.layout.addWidget(self.fps_label)
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(10)
        self.fps_slider.setMaximum(100)
        self.fps_slider.setValue(60)
        self.fps_slider.valueChanged.connect(self.on_fps_change)
        self.layout.addWidget(self.fps_slider)

        self.setLayout(self.layout)
        self.is_paused = False

    def toggle_pause(self):
        """Toggles the pause state of the simulation."""
        self.is_paused = not self.is_paused
        self.pause_button.setText("Restart" if self.is_paused else "Pause")
        self.pause_toggled.emit()

    def on_fps_change(self, value):
        """Handles the FPS slider value change."""
        self.fps_label.setText(f"FPS: {value}")
        self.fps_changed.emit(value)
