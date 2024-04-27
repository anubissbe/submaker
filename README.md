Setup Guide for Subtitle Translation and Transcription Script
=============================================================

This document provides the instructions to set up and use the subtitle translation and transcription script, designed to handle video files for subtitle generation and translation.

Requirements
------------

The script requires the following tools and libraries:

*   Python 3.8+
*   FFmpeg
*   Argos Translate
*   Whisper AI Model
*   FastAPI
*   Uvicorn
*   Requests library for Python

Installation
------------

Follow these steps to install necessary components:

### 1\. FFmpeg

Install FFmpeg on your system. For Ubuntu:

sudo apt update
sudo apt install ffmpeg

### 2\. Python Libraries

Install the required Python libraries using pip:

pip install argostranslate fastapi uvicorn whisper requests

### 3\. Set Up Whisper AI

Ensure Whisper AI is properly installed and configured:

python -m whisper.download

Setting Up the Server
---------------------

To run the transcription service using Whisper AI:

uvicorn whisper\_server:app --host 0.0.0.0 --port 8000

Running the Script
------------------

Once all services are up and running, you can execute the script as follows:

python3 addsubs.py

Script Functionality
--------------------

The script processes video files to:

*   Check existing subtitles in Arabic, Dutch, or English.
*   Translate missing subtitle languages using Argos Translate.
*   If no subtitles exist, extract audio and use Whisper AI for transcription.

Configuration Details
---------------------

The script assumes video and subtitle files are located in a specific directory (e.g., `/mnt/media/complete/`). Adjust the path in the script as necessary to fit your directory structure.

Contact Support
---------------

If you encounter any issues, please contact bert@telkom.be for assistance.# submaker
