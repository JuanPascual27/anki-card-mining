import vlc
import pysubs2
from PyQt5.QtWidgets import (
    QMainWindow, 
    QPushButton, 
    QLabel, 
    QListWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QSlider, 
    QWidget, 
    QTextEdit,
)
from PyQt5.QtCore import Qt, QTimer

from makeAnkiDeck import export_to_anki

class VolumeControl(QWidget):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player

        # Volume slider
        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Float Style
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(40, 120)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.volume_slider)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Timer to hide volumen control if is not under mouse 
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(250)
        self.hide_timer.timeout.connect(self.check_mouse_leave)

    def set_volume(self, value):
        self.player.audio_set_volume(value)

    def check_mouse_leave(self):
        if not self.underMouse() and not self.parentWidget().underMouse():
            self.hide()
            self.hide_timer.stop()

class VolumeButton(QPushButton):
    def __init__(self, player, parent=None):
        super().__init__("🔊", parent)
        self.setFixedSize(30, 30)
        self.volume_control = VolumeControl(player, self)

    def enterEvent(self, event):
        button_pos = self.mapToGlobal(self.rect().topLeft())
        self.volume_control.move(button_pos.x() - 5, button_pos.y() - self.volume_control.height())
        self.volume_control.show()
        self.volume_control.hide_timer.start()

    def leaveEvent(self, event):
        if not self.volume_control.underMouse():
            self.volume_control.hide_timer.start()

class VideoSubtitleEditor(QMainWindow):
    def __init__(self, parent, video_path, subtitle_path, output):
        super().__init__()
        self.setWindowTitle("Sentence Mining")
        self.setGeometry(50, 50, 800, 600)

        # VLC Instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # EndReached Event
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Video widget
        self.video_widget = QLabel(self)
        self.player.set_hwnd(self.video_widget.winId())  # Windows only

        # Progress bar
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setToolTip("Position")
        self.slider.sliderMoved.connect(self.set_position)
        self.rewind_button = QPushButton("⏪10s")
        self.rewind_button.clicked.connect(self.rewind_10_seconds)
        self.play_button = QPushButton("▶️")
        self.play_button.clicked.connect(self.play_pause_video)
        self.forward_button = QPushButton("10s⏩")
        self.forward_button.clicked.connect(self.forward_10_seconds)
        
        # Volume controls
        self.volume_button = VolumeButton(self.player)
        
        # Timer
        self.time_label = QLabel("00:00 / 00:00")

        # Buttons
        self.start_button = QPushButton("Set Start")
        self.start_button.clicked.connect(self.mark_start)

        self.end_button = QPushButton("Set End")
        self.end_button.clicked.connect(self.mark_end)

        self.add_fragment_button = QPushButton("Add Fragment")
        self.add_fragment_button.clicked.connect(self.add_fragment)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.setDisabled(True)
        self.save_changes_button.clicked.connect(self.save_changes)

        self.export_button = QPushButton("Export to Anki")
        self.export_button.clicked.connect(self.export_to_anki)

        self.go_back_button = QPushButton("Back to Downloader")
        self.go_back_button.clicked.connect(self.go_back)

        # List of sentences
        self.fragment_list = QListWidget()
        self.fragment_list.itemClicked.connect(self.select_fragment)

        # Field to edit current fragment sentence and meaning
        self.subtitle_editor = QTextEdit()
        self.subtitle_editor.setPlaceholderText("Edit Fragment Sentence")
        self.meaning = QTextEdit()
        self.meaning.setPlaceholderText("Write Sentence Meaning")

        # Layout
        main_layout = QVBoxLayout()

        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_widget, 480)

        # Layout for slider and buttons
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.rewind_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.forward_button)
        control_layout.addWidget(self.volume_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.time_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.end_button)
        button_layout.addWidget(self.add_fragment_button)
        button_layout.addWidget(self.export_button)

        button_layout_2 = QHBoxLayout()
        button_layout_2.addWidget(self.go_back_button)
        button_layout_2.addWidget(self.save_changes_button)

        main_layout.addLayout(video_layout, 480)
        main_layout.addLayout(control_layout, 20)
        main_layout.addLayout(button_layout, 50)
        main_layout.addWidget(QLabel("Selected Fragments:"))
        main_layout.addWidget(self.fragment_list, 50)
        main_layout.addWidget(QLabel("Sentence:"))
        main_layout.addWidget(self.subtitle_editor, 10)
        main_layout.addWidget(self.meaning, 10)
        
        main_layout.addLayout(button_layout_2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Variables
        self.p = parent
        self.video_path = video_path
        self.subtitle_path = subtitle_path
        self.output_path = output
        self.start_time = None
        self.end_time = None
        self.fragments = []
        self.current_fragment_index = None

        # Load video
        self.set_video(self.video_path)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(500) 

    def set_video(self, video_path):
        media = self.instance.media_new(video_path)
        self.player.set_media(media)
        self.player.play()
        # Wait to load video in vlc
        QTimer.singleShot(150, self.set_slider_range)

    def set_slider_range(self):
        self.player.pause()
        duration = self.player.get_length()
        if duration > 0:
            self.slider.setRange(0, duration)

    def play_pause_video(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setText("▶️")
        else:
            self.player.play()
            self.play_button.setText("⏸️")

    def rewind_10_seconds(self):
        current_time = self.player.get_time()
        new_time = max(0, current_time - 10000)
        self.player.set_time(new_time)
        self.slider.setValue(new_time)

    def forward_10_seconds(self):
        current_time = self.player.get_time()
        duration = self.player.get_length()
        new_time = min(duration, current_time + 10000)
        self.player.set_time(new_time)
        self.slider.setValue(new_time)

    def set_position(self, position):
        self.player.set_time(position)
    
    def update_time(self):
        current_time = self.player.get_time()
        duration = self.player.get_length()

        if current_time >= 0 and duration > 0:
            self.slider.setValue(current_time)
            formatted_current_time = self.format_time(current_time)
            formatted_duration = self.format_time(duration)
            self.time_label.setText(f"{formatted_current_time} / {formatted_duration}")
    
    @staticmethod
    def format_time(ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"
    
    def on_video_end(self, event):
        QTimer.singleShot(0, self.handle_video_end)

    def handle_video_end(self):
        self.timer.stop()
        self.slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        self.player.stop()
        self.set_video(self.video_path)

    def mark_start(self):
        self.start_time = self.player.get_time() / 1000 # Secs

    def mark_end(self):
        self.end_time = self.player.get_time() / 1000 # Secs

    def add_fragment(self):
        if self.start_time is not None and self.end_time is not None:
            subs = pysubs2.load(self.subtitle_path)
            fragment_subtitles = [
                line.text for line in subs if line.start / 1000 < self.end_time and line.end / 1000 > self.start_time
            ]
            combined_subtitles = " ".join(fragment_subtitles) if fragment_subtitles else ""
            fragment = {
                "start": self.start_time,
                "end": self.end_time,
                "subtitles": combined_subtitles,
                "meaning": ""
            }
            self.fragments.append(fragment)
            self.fragment_list.addItem(f"Start: {self.start_time:.2f}s - End: {self.end_time:.2f}s")
            item = self.fragment_list.item(len(self.fragments)-1)
            self.fragment_list.setCurrentItem(item)
            self.fragment_list.itemClicked.emit(item)

    def select_fragment(self, item):
        index = self.fragment_list.row(item)
        self.save_changes_button.setDisabled(False)
        if index < len(self.fragments):
            self.current_fragment_index = index
            fragment = self.fragments[index]
            self.subtitle_editor.setText(fragment["subtitles"])
            self.meaning.setText(fragment["meaning"])
    
    def save_changes(self):
        if self.current_fragment_index is not None:
            updated_subtitle = self.subtitle_editor.toPlainText()
            meaning = self.meaning.toPlainText()
            self.fragments[self.current_fragment_index]["subtitles"] = updated_subtitle
            self.fragments[self.current_fragment_index]["meaning"] = meaning
            self.save_changes_button.setDisabled(True)
            self.current_fragment_index = None
            self.subtitle_editor.setText("")
            self.meaning.setText("")
    
    def export_to_anki(self):
        export_to_anki(2059400110, "English Learning::Sentences Mining", self.fragments, self.video_path)
    
    def go_back(self):
        self.player.stop()
        self.p.show()
        self.close()