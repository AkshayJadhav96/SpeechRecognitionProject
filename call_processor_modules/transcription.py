"""Module for transcribing audio segments using a specified transcription model.

This module processes audio files, extracts the required segments, and
performs transcription, returning the transcribed text.

The `transcribe_audio_segment` function extracts an audio segment from the
provided file based on the specified start and end times (if available),
performs transcription, and returns the resulting text.
"""

from pathlib import Path

from pydub import AudioSegment

from call_processor_modules.pydantic_models import (
    TranscribeAudioSegmentInput,
    TranscribeAudioSegmentOutput,
)
from logger_config import get_logger

from . import model

logger = get_logger()


def transcribe_audio_segment(
    data: TranscribeAudioSegmentInput) -> TranscribeAudioSegmentOutput:
    """Extract and transcribe an audio segment from a file.

    This function extracts an audio segment based on the provided start and end
    times (or uses the full file if no times are given) and performs transcription
    on the segment using the specified transcription model.

    :param data: Contains audio file path and optional start/end times for the
                 segment to be transcribed.
    :type data: TranscribeAudioSegmentInput
    :return: The transcription result of the extracted audio segment.
    :rtype: TranscribeAudioSegmentOutput
    """
    try:
        logger.info("Starting transcription for file: {data.audio_file}")

        # Load audio file
        audio = AudioSegment.from_file(data.audio_file)

        # Extract segment if start and end times are provided
        if data.start_time and data.end_time:
            segment = audio[data.start_time * 1000:data.end_time * 1000]
            logger.info("Extracted segment from {data.start_time}s to {data.end_time}s")
        else:
            segment = audio
            logger.info("Using full audio file for transcription.")

        # Export segment as a temporary WAV file
        temp_wav_path = "temp_segment.wav"
        segment.export(temp_wav_path, format="wav")
        logger.info("Temporary WAV file created: {temp_wav_path}")

        # Perform transcription
        result = model.transcribe(temp_wav_path)

        # Remove temporary file
        Path.unlink(temp_wav_path)
        logger.info("Temporary file deleted: {temp_wav_path}")

        # Extract transcription result
        transcription = result["text"]
        logger.info("Transcription successful: {transcription[:50]}...")

        return TranscribeAudioSegmentOutput(transcription=transcription)

    except Exception:
        logger.exception("Error during transcription")
        return TranscribeAudioSegmentOutput(transcription="False")


