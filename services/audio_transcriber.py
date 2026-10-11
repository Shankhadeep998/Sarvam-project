import os
from typing import Optional, Union, BinaryIO
from services.sarvam_client import get_sarvam_client

def transcribe_audio(
    audio_file: Union[str, BinaryIO, bytes],
    filename: str = "lecture_audio.mp3",
    language_code: str = "unknown",
    mode: str = "codemix",
    model: str = "saaras:v3"
) -> dict:
    """
    Transcribes lecture audio using Sarvam AI Saaras v3 model.
    Handles Indic languages, English, and code-mixed speech (e.g. Hinglish).

    :param audio_file: Path to audio file, file-like object, or raw bytes.
    :param filename: Name of the audio file (including extension like .mp3, .wav, .m4a).
    :param language_code: BCP-47 language code (e.g. 'hi-IN', 'en-IN', or 'unknown' for auto-detection).
    :param mode: 'codemix', 'transcribe', or 'verbatim'.
    :param model: Speech-to-text model name (default: 'saaras:v3').
    :return: dict with 'transcript', 'language_code', 'language_probability', 'request_id'.
    """
    client = get_sarvam_client()
    
    # If audio_file is a file path string
    if isinstance(audio_file, str):
        with open(audio_file, "rb") as f:
            file_data = f.read()
    elif isinstance(audio_file, bytes):
        file_data = audio_file
    else:
        # File-like object (e.g. Streamlit UploadedFile)
        file_data = audio_file.read()

    response = client.speech_to_text.transcribe(
        file=(filename, file_data, "audio/mpeg"),
        model=model,
        mode=mode,
        language_code=language_code,
        with_timestamps=False,
    )

    return {
        "transcript": response.transcript,
        "language_code": getattr(response, "language_code", language_code),
        "language_probability": getattr(response, "language_probability", None),
        "request_id": getattr(response, "request_id", None),
    }
