import os
import genanki
import hashlib
from datetime import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip

def export_to_anki(deck_id, deck_name, fragments, video_path):
    if not fragments:
        print("No hay fragmentos seleccionados para exportar.")
        return
    
    deck = genanki.Deck(deck_id, deck_name)
    media_files = []
    for i, fragment in enumerate(fragments):
        start, end = fragment["start"], fragment["end"]

        # Generar el fragmento de video
        video_file = generate_unique_filename("card", "webm")
        video_clip = VideoFileClip(video_path).subclipped(start, end)
        video_clip.write_videofile(video_file, codec="libvpx", audio_codec='libvorbis')
        media_files.append(video_file)

        # Generar el fragmento de audio
        audio_file = generate_unique_filename("card", "ogg")
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_file, codec='libvorbis')
        media_files.append(audio_file)

        sentence = fragment['subtitles']
        meaning = fragment['meaning']

        # Crear la tarjeta de Anki
        note = genanki.Note(
            model=genanki.Model(
                1607392319,
                "Multimedia Model",
                fields=[
                    {"name": "Audio"},
                    {"name": "Video"},
                    {"name": "Sentence"},
                    {"name": "Meaning"}
                ],
                templates=[
                    {
                        "name": "Multimedia Card 1",
                        "qfmt": """
                            <div class="container">
                                <div class="spaced sentence">{{Sentence}}</div>
                            </div>
                        """,
                        "afmt": """
                            <div class="container">
                                <div class="spaced">{{FrontSide}}</div>
                                <hr>
                                <div class="spaced meaning">{{Meaning}}</div>
                                <div class="spaced">{{Audio}}</div>
                                <div class="spaced">{{Video}}</div>
                            </div>
                        """
                    },
                    {
                        "name": "Multimedia Card 2",
                        "qfmt": """
                            <div class="container">
                                <div class="spaced">{{Audio}}</div>
                            </div>
                        """,
                        "afmt": """
                            <div class="container">
                                <div class="spaced">{{FrontSide}}</div>
                                <hr>
                                <div class="spaced sentence">{{Sentence}}</div>
                                <div class="spaced meaning">{{Meaning}}</div>
                                <div class="spaced">{{Video}}</div>
                            </div>
                        """
                    },
                    {
                        "name": "Multimedia Card 3",
                        "qfmt": """
                            <div class="container">
                                <div class="spaced">{{Video}}</div>
                            </div>
                        """,
                        "afmt": """
                            <div class="container">
                                <div class="spaced">{{FrontSide}}</div>
                                <hr>
                                <div class="spaced sentence">{{Sentence}}</div>
                                <div class="spaced meaning">{{Meaning}}</div>
                                <div class="spaced">{{Audio}}</div>
                            </div>
                        """
                    },
                    {
                        "name": "Multimedia Card 4",
                        "qfmt": """
                            <div class="container">
                                <div class="spaced meaning">{{Meaning}}</div>
                            </div>
                        """,
                        "afmt": """
                            <div class="container">
                                <div class="spaced">{{FrontSide}}</div>
                                <hr>
                                <div class="spaced sentence">{{Sentence}}</div>
                                <div class="spaced">{{Audio}}</div>
                                <div class="spaced">{{Video}}</div>
                            </div>
                        """
                    },
                    {
                        "name": "Multimedia Card 5",
                        "qfmt": """
                            <div class="container">
                                <div class="spaced sentence">{{Sentence}}</div>
                                <div class="spaced">{{Audio}}</div>
                            </div>
                        """,
                        "afmt": """
                            <div class="container">
                                <div class="spaced">{{FrontSide}}</div>
                                <hr>
                                <div class="spaced meaning">{{Meaning}}</div>
                                <div class="spaced">{{Video}}</div>
                            </div>
                        """
                    }
                ],
                css="""
                    <style>
                        .container {
                            text-align: center;
                        }
                        .spaced {
                            margin-bottom: 20px;
                        }
                        hr {
                            margin-bottom: 20px;
                        }
                        .sentence {
                            font-size: 24px;
                            font-weight: bold;
                        }
                        .meaning {
                            font-size: 20px;
                            font-weight: bold;
                        }
                    </style>
                """
            ),
            fields=[
                f'<audio controls src="{audio_file}" type="audio/ogg"></audio>',
                f'<video controls src="{video_file}" type="video/webm"></video>',
                sentence,
                meaning
            ],
            guid=generate_guid(sentence)
        )
        deck.add_note(note)

    # Crear el paquete Anki e incluir los archivos multimedia
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file("multimedia_cards.apkg")

    # Limpieza opcional: eliminar archivos temporales
    for file in media_files:
        os.remove(file)
    
def generate_guid(sentence):
    return hashlib.md5(sentence.encode('utf-8')).hexdigest()

def generate_unique_filename(prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"
