"""Module for performing speaker diarization on audio files.

This module uses the pyannote.audio library to identify
speakers in an audio file and generates
metrics such as speaker segments, speaking ratio, interruptions, and time to
first token.

Functions:
    - raise_error: Helper function to raise a ValueError with a custom message.
    - diarize: Performs speaker diarization on the provided audio file,
      identifies speakers, and computes speaker-related metrics.
"""

import os

import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline

from call_processor_modules.pydantic_models import (
    DiarizeInput,
    DiarizeOutput,
    SpeakerSegment,
)
from logger_config import get_logger

load_dotenv()
logger = get_logger()

def raise_error(message: str) -> None:
    """Raise a ValueError with the given message."""
    raise ValueError(message)

def diarize(data: DiarizeInput) -> DiarizeOutput:
    """Perform speaker diarization on the given audio file.

    This function uses the pyannote.audio pipeline to perform speaker diarization,
    processes the audio file, and computes metrics like speaker segments, speaking
    ratio, interruptions, and the time to first token.

    :param data: The input data containing the path to the audio file for diarization.
    :type data: DiarizeInput
    :return: The output data containing speaker segments, speaking ratio,
             interruptions, and time to first token.
    :rtype: DiarizeOutput
    :raises ValueError: If the Hugging Face token is not found in environment variables.
    """
    # Initialize variables to avoid UnboundLocalError
    speaker_segments = []
    speaking_ratio = "N/A (only one speaker detected)"
    interruptions = 0
    first_speaker_time = 0.0

    try:
        audio_file = data.audio_file
        logger.info("Starting speaker diarization for file: {audio_file}")

        token = os.getenv("HUGGING_FACE_TOKEN")
        if not token:
            error_text = "Hugging Face token not found in environment variables."
            raise_error(error_text)

        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                            use_auth_token=token)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        pipeline.to(device)
        logger.info("Pipeline loaded and moved to {device}")

        diarization = pipeline(audio_file)
        speaker_segments = []

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append(SpeakerSegment(
                speaker=speaker,
                start_time=turn.start,
                end_time=turn.end,
            ))

        logger.info("Identified {len(speaker_segments)} speaker segments")

        # Compute metrics
        total_time = {}
        interruptions = 0
        first_speaker_time = None
        prev_speaker = None
        prev_end_time = 0

        for segment in speaker_segments:
            start, end, speaker = segment.start_time, segment.end_time, segment.speaker
            duration = end - start
            total_time[speaker] = total_time.get(speaker, 0) + duration

            if prev_speaker and prev_speaker != speaker and start < prev_end_time:
                interruptions += 1

            if first_speaker_time is None:
                first_speaker_time = start

            prev_speaker = speaker
            prev_end_time = end
        least_len = 2
        if len(total_time) >= least_len:
            speakers = list(total_time.keys())
            speaking_ratio = total_time[speakers[0]] / total_time[speakers[1]]
        else:
            speaking_ratio = "N/A (only one speaker detected)"
            logger.warning("Only One Speaker Detected")

        logger.warning("Speaking ratio: {speaking_ratio}")
        logger.info("Interruptions count: {interruptions}")
        logger.info("Time to first token: {first_speaker_time or 0.0}")

    except Exception:
        logger.exception("Error in speaker Diarization : {e!s}")

    return DiarizeOutput(
        speaker_segments=speaker_segments,
        speaking_ratio=speaking_ratio,
        interruptions=interruptions,
        time_to_first_token=first_speaker_time or 0.0,
    )
