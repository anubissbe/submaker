import os
import subprocess
import requests
from pathlib import Path
import argostranslate.package, argostranslate.translate
from langdetect import detect

# Define the base directory for video files
BASE_DIRECTORY = "/mnt/media/complete/"

# API URL for the Whisper server
WHISPER_SERVER_URL = "http://localhost:8000/transcribe"

# Define valid video file extensions
VIDEO_EXTS = ['.mp4', '.mkv', '.avi', '.m2ts', '.mov', '.wmv', '.flv', '.mpg',
              '.mpeg', '.vob', '.rm', '.rmvb', '.3gp', '.divx', '.xvid', '.webm']

# Initialize Argos Translate
languages = argostranslate.translate.get_installed_languages()
language_pairs = {f"{lang_from.code}-{lang_to.code}": lang_from.get_translation(lang_to)
                  for lang_from in languages for lang_to in languages
                  if lang_from.code != lang_to.code}

def translate_subtitle(input_path, from_lang, to_lang):
    """Translates subtitle files from one language to another."""
    output_path = Path(str(input_path).replace(f".{from_lang}.srt", f".{to_lang}.srt"))
    if output_path.exists():
        return  # Skip if translation already exists
    
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    translation = language_pairs[f"{from_lang}-{to_lang}"].translate(content)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(translation)
    print(f"Translated {input_path} from {from_lang} to {to_lang}")

def transcribe_audio(audio_path):
    """Send audio file to Whisper server and receive transcription."""
    with open(audio_path, 'rb') as file:
        response = requests.post(WHISPER_SERVER_URL, files={'file': file})
    return response.json()['transcription']

def extract_audio(video_path):
    """Extract audio from video file to use for transcription."""
    audio_path = video_path.with_suffix('.mp3')
    if not audio_path.exists():
        command = ['ffmpeg', '-i', str(video_path), '-vn', '-acodec', 'mp3', str(audio_path)]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return audio_path

def process_video_file(video_path):
    """Process a single video file to handle subtitles."""
    has_subs = {lang: False for lang in ['en', 'ar', 'nl']}
    for sub_ext in ['.en.srt', '.ar.srt', '.nl.srt']:
        if (video_path.with_suffix(sub_ext)).exists():
            has_subs[sub_ext[1:3]] = True

    if all(has_subs.values()):
        return  # All required subtitles exist

    if not any(has_subs.values()):  # No subtitles, extract and transcribe
        audio_path = extract_audio(video_path)
        transcription = transcribe_audio(audio_path)
        for lang_code in ['en', 'ar', 'nl']:
            sub_path = video_path.with_suffix(f'.{lang_code}.srt')
            with open(sub_path, 'w', encoding='utf-8') as file:
                file.write(transcription)
            print(f"Transcribed audio to {sub_path}")
    else:
        for lang_code, exists in has_subs.items():
            if not exists:
                # Find existing subtitle file
                existing_sub = next((p for p in has_subs if has_subs[p]), None)
                translate_subtitle(video_path.with_suffix(f'.{existing_sub}.srt'), existing_sub[:2], lang_code)

def main():
    """Main function to walk through directories and process video files."""
    for dirpath, _, filenames in os.walk(BASE_DIRECTORY):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in VIDEO_EXTS:
                process_video_file(file_path)

if __name__ == "__main__":
    main()

