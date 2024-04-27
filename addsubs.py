import os
import subprocess
from pathlib import Path
import requests
import argostranslate.translate
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load installed Argostranslate languages
languages = argostranslate.translate.get_installed_languages()
translation_models = {f"{lang_from.code}-{lang_to.code}": lang_from.get_translation(lang_to)
                      for lang_from in languages for lang_to in languages if lang_from != lang_to}

def translate_subtitle(input_path, output_path, from_lang, to_lang):
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            content = file.read()
        translated_content = translation_models[f"{from_lang}-{to_lang}"].translate(content)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        logging.info(f"Translated {input_path} from {from_lang} to {to_lang}")
    except KeyError:
        logging.error(f"No translation model found for {from_lang} to {to_lang}")

def extract_audio(video_path, audio_output_path):
    try:
        command = ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "mp3", str(audio_output_path)]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info(f"Extracted audio to {audio_output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to extract audio from {video_path}: {e}")

def transcribe_audio(audio_path):
    try:
        url = "http://localhost:8001/transcribe"
        with open(audio_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
        transcription = response.json()['transcription']
        logging.info(f"Transcribed audio {audio_path}")
        return transcription
    except Exception as e:
        logging.error(f"Failed to transcribe {audio_path}: {e}")
        return ""

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in ['.mp4', '.mkv', '.avi', '.m2ts', '.mov', '.wmv', '.flv', '.mpg', '.mpeg', '.vob', '.rm', '.rmvb', '.3gp', '.divx', '.xvid', '.webm']:
                base_name = file_path.stem
                audio_path = file_path.with_suffix('.mp3')
                sub_paths = {lang: file_path.parent / f"{base_name}.{lang}.srt" for lang in ['en', 'ar', 'nl']}
                
                # Check and generate missing subtitles through translation
                existing_subs = {lang: path for lang, path in sub_paths.items() if path.exists()}
                missing_langs = [lang for lang in ['en', 'ar', 'nl'] if lang not in existing_subs.keys()]
                
                # Translate existing subtitles to missing languages if possible
                for existing_lang, existing_path in existing_subs.items():
                    for missing_lang in missing_langs:
                        if f"{existing_lang}-{missing_lang}" in translation_models:
                            translate_subtitle(existing_path, sub_paths[missing_lang], existing_lang, missing_lang)
                
                # If no subtitles exist, transcribe using Whisper
                if not existing_subs:
                    if not audio_path.exists():
                        extract_audio(file_path, audio_path)
                    transcription = transcribe_audio(audio_path)
                    # Create subtitles for each required language (assuming English transcription first)
                    with open(sub_paths['en'], 'w') as f:
                        f.write(transcription)
                    translate_subtitle(sub_paths['en'], sub_paths['ar'], 'en', 'ar')
                    translate_subtitle(sub_paths['en'], sub_paths['nl'], 'en', 'nl')

if __name__ == "__main__":
    process_directory('/mnt/media/complete/')

