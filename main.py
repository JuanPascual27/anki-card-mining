from PyQt5.QtWidgets import QApplication

from YoutubeDownloader import YouTubeDownloader

# https://www.youtube.com/watch?v=MeqOtGHtqNY last: 2:57 "Better late than never"
if __name__ == "__main__":
    app = QApplication([])
    style = """
        QWidget {
            background-color: #2E2E2E;  /* Fondo oscuro */
            color: #FFFFFF;             /* Texto blanco */
        }

        QPushButton {
            background-color: #4C4C4C;  /* Fondo gris oscuro para botones */
            color: white;               /* Texto blanco */
            border: 1px solid #666666;  /* Borde gris */
            border-radius: 5px;         /* Bordes redondeados */
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #6A6A6A;  /* Fondo más claro al pasar el mouse */
        }

        QLabel {
            background-color: #333333;  /* Fondo gris oscuro para etiquetas */
            color: white;               /* Texto blanco */
            padding: 5px;
            font-size: 16px;
        }

        QLineEdit {
            background-color: #555555;  /* Fondo gris oscuro para cuadros de texto */
            color: #FFFFFF;             /* Texto blanco */
            border: 1px solid #888888;  /* Borde gris */
            padding: 5px;
        }

        QLineEdit:focus {
            border: 1px solid #00009F;  /* Borde naranja cuando el cuadro de texto está enfocado */
        }
    """
    app.setStyleSheet(style)
    downloader = YouTubeDownloader()
    downloader.show()
    app.exec_()
