from call_processor_modules.pydantic_models import TranscribeAudioSegmentInput, TranscribeAudioSegmentOutput
from pydub import AudioSegment
from . import model

from logger_config import get_logger
logger = get_logger()
import os

def transcribe_audio_segment(data: TranscribeAudioSegmentInput) -> TranscribeAudioSegmentOutput:

    try:
        logger.info(f"Starting transcription for file: {data.audio_file}")

        # Load audio file
        audio = AudioSegment.from_file(data.audio_file)

        # Extract segment if start and end times are provided
        if data.start_time and data.end_time:
            segment = audio[data.start_time * 1000:data.end_time * 1000]
            logger.info(f"Extracted segment from {data.start_time}s to {data.end_time}s")
        else:
            segment = audio
            logger.info("Using full audio file for transcription.")

        # Export segment as a temporary WAV file
        temp_wav_path = "temp_segment.wav"
        segment.export(temp_wav_path, format="wav")
        logger.info(f"Temporary WAV file created: {temp_wav_path}")

        # Perform transcription
        result = model.transcribe(temp_wav_path)
        
        # Remove temporary file
        os.remove(temp_wav_path)
        logger.info(f"Temporary file deleted: {temp_wav_path}")

        # Extract transcription result
        transcription = result["text"]
        logger.info(f"Transcription successful: {transcription[:50]}...")  # Log first 50 chars

        return TranscribeAudioSegmentOutput(transcription=transcription)

    except Exception as e:
        logger.exception("Error during transcription")
        return TranscribeAudioSegmentOutput(transcription="False")


