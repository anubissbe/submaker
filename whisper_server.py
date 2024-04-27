import os
import whisper
from fastapi import FastAPI, File, UploadFile
import uvicorn

# Set the GPU device to use only GPU 1
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

app = FastAPI()

# Load the "large" Whisper model on the specified GPU
model = whisper.load_model("large")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Endpoint to receive an audio file and return its transcription using Whisper large model."""
    audio_data = await file.read()
    temp_file_path = "temp_audio.ogg"
    with open(temp_file_path, "wb") as audio_file:
        audio_file.write(audio_data)

    # Use the Whisper model to transcribe the audio
    result = model.transcribe(temp_file_path)
    return {"transcription": result['text']}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)

