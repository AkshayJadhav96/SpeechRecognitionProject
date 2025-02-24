"""Module for calculating the speaking speed (words per minute) for each speaker.

Based on their speech data, this module processes speaker segments and computes
the speaking speed for each speaker from the provided speaker speech data.
The `calculate_speaking_speed` function calculates the speaking speed for each
speaker and returns the results in a dictionary.
"""

from call_processor_modules.pydantic_models import (
    CalculateSpeakingSpeedOutput,
    SpeakerSpeechData,
)
from logger_config import get_logger

logger = get_logger()

def calculate_speaking_speed(
    input_speech_data: SpeakerSpeechData) -> CalculateSpeakingSpeedOutput:
    """Calculate the speaking speed(words per minute) for each speaker.

    param data: Contains speaker segments and audio file path.
    return: Speaking speeds in words per minute for each speaker.

    """
    try:
        speaker_speech_data = input_speech_data.speaker_speech_data
        speaking_speeds = {
            speaker: (data.length / data.time_period) * 60
            if data.time_period > 0 else 0
            for speaker, data in speaker_speech_data.items()
        }

        logger.info("Calculated Speaking Speeds: {speaking_speeds}")

        return CalculateSpeakingSpeedOutput(speaking_speeds=speaking_speeds)

    except Exception:
        logger.exception("Error in calculate_speaking_speed")
        return CalculateSpeakingSpeedOutput(speaking_speeds={})
