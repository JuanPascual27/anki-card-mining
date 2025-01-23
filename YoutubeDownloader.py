import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from VideoSubtitleEditor import VideoSubtitleEditor
from getYoutubeVideo import download_video
from systemHelpers import create_temp_dir

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, str, str)  # video, subtitles, temp

    def __init__(self, url, output, lang):
        super().__init__()
        self.url = url
        self.output = output
        self.lang = lang

    def run(self):
        try:
            self.progress_signal.emit("Initiating Download......")
            video_path = download_video(self.url, self.output, self.lang)
            subtitles_path = os.path.join(self.output, f"video.{self.lang}.srt")
            self.progress_signal.emit("Download Complete")
            self.finished_signal.emit(video_path, subtitles_path, self.output)
        except Exception as e:
            self.progress_signal.emit(f"Error: {e}")


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Download Youtube Video")
        self.setGeometry(100, 100, 400, 200)

        # Widgets
        self.label = QLabel("Youtube URL:")
        self.url_input = QLineEdit()
        self.label = QLabel("Subtitles language:")
        self.lang = QLineEdit()
        self.download_button = QPushButton("Download")
        self.status_label = QLabel("")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.lang)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.download_button.clicked.connect(self.iniciar_descarga)

    def iniciar_descarga(self):
        url = self.url_input.text().strip()
        lang = self.lang.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please, set valid URL.")
            return
        
        output_dir = create_temp_dir()

        self.status_label.setText("Initiating Download...")
        self.download_thread = DownloadThread(url, output_dir, lang)
        self.download_thread.progress_signal.connect(self.actualizar_estado)
        self.download_thread.finished_signal.connect(self.finalizar_descarga)
        self.download_thread.start()

    def actualizar_estado(self, mensaje):
        self.status_label.setText(mensaje)

    def finalizar_descarga(self, video_path, subtitles_path, output):
        if "Error" in self.status_label.text():
            QMessageBox.critical(self, "Error", self.status_label.text())
        else:
            QMessageBox.information(self, "Success", "Complete Video Download.")
            self.abrir_editor(video_path, subtitles_path, output)

    def abrir_editor(self, video_path, subtitles_path, output):
        self.editor = VideoSubtitleEditor(self, video_path, subtitles_path, output)
        self.editor.show()
        self.hide()
