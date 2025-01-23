import os
import re
from yt_dlp import YoutubeDL

def download_video(url: str, output: str, lang: str):
    video_path = os.path.join(output, "video.webm")
    ydl_opts = {
        #'format': 'bestvideo+bestaudio/best',
        #'merge_output_format': 'mp4',
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'subtitleslangs': [lang],
        'outtmpl': video_path,
        'ffmpeg_location': './tools/ffmpeg/ffmpeg.exe'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "subtitles" in info and lang in info["subtitles"]:
                ydl_opts['writesubtitles'] = True
            elif "automatic_captions" in info and lang in info["automatic_captions"]:
                ydl_opts.update({
                    'writesubtitles': True,
                    'writeautomaticsub': True
                })
            else:
                print("Error con los subtitulos")
                
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
            vtt_path = os.path.join(output, f"video.{lang}.vtt")
            srt_path = os.path.join(output, f"video.{lang}.srt")
            convert_vtt_to_srt(vtt_path, srt_path)

    except Exception as e:
        print(f"Error al descargar video: {e}")
    
    return video_path

def download_audio(url: str, output: str):
    audio_path = os.path.join(output, "audio")
    ydl_opts = {
        'format': 'wav/bestaudio/best',
        'ffmpeg_location': './tools/ffmpeg/ffmpeg.exe',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': audio_path,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    return audio_path

def convert_vtt_to_srt(vtt_file, srt_file, delete_vtt=True):
    with open(vtt_file, "r", encoding="utf-8") as vtt, open(srt_file, "w", encoding="utf-8") as srt:
        counter = 0
        buffer = []
        for line in vtt:
            if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:") or line.strip() == "":
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
                if buffer:
                    srt.write(f"{counter}\n")
                    srt.write("\n".join(buffer) + "\n\n")
                    buffer = []
                counter += 1
                line = line.replace(".", ",")
                buffer.append(line.strip())
                continue
            clean_line = re.sub(r"<.*?>", "", line).strip()
            if clean_line:
                buffer.append(clean_line)
        if buffer:
            srt.write(f"{counter}\n")
            srt.write("\n".join(buffer) + "\n\n")

    if delete_vtt:
        os.remove(vtt_file)