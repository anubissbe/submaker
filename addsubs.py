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
                  if lang_from.code in ['en', 'ar', 'nl'] and lang_to.code in ['en', 'ar', 'nl']}

def translate_subtitle(input_text, from_lang, to_lang):
    """Translates text from one language to another."""
    translation = language_pairs[f"{from_lang}-{to_lang}"].translate(input_text)
    return translation

def transcribe_audio(audio_path, lang='en'):
    """Send audio file to Whisper server and receive transcription."""
    with open(audio_path, 'rb') as file:
        response = requests.post(f"{WHISPER_SERVER_URL}/{lang}", files={'file': file})
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
    subtitles_exist = {lang: video_path.with_suffix(f'.{lang}.srt').exists() for lang in ['en', 'ar', 'nl']}

    if not any(subtitles_exist.values()):  # No subtitles, extract and transcribe
        audio_path = extract_audio(video_path)
        # Transcribe and translate
        for lang_code in ['en', 'ar', 'nl']:
            transcription = transcribe_audio(audio_path, lang_code)
            sub_path = video_path.with_suffix(f'.{lang_code}.srt')
            with open(sub_path, 'w', encoding='utf-8') as file:
                file.write(transcription)
            print(f"Transcribed audio to {sub_path}")
    else:
        base_lang = next((lang for lang, exists in subtitles_exist.items() if exists), None)
        base_sub_path = video_path.with_suffix(f'.{base_lang}.srt')
        with open(base_sub_path, 'r', encoding='utf-8') as file:
            base_content = file.read()

        # Translate missing subtitles
        for lang_code, exists in subtitles_exist.items():
            if not exists:
                translated_content = translate_subtitle(base_content, base_lang, lang_code)
                new_sub_path = video_path.with_suffix(f'.{lang_code}.srt')
                with open(new_sub_path, 'w', encoding='utf-8') as file:
                    file.write(translated_content)
                print(f"Translated {base_sub_path} to {new_sub_path}")

def main():
    """Main function to walk through directories and process video files."""
    for dirpath, _, filenames in os.walk(BASE_DIRECTORY):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in VIDEO_EXTS:
                process_video_file(file_path)

if __name__ == "__main__":
    main()

