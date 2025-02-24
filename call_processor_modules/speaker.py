"""Module for processing speaker segments data for each speaker in an audio file.

This module computes the total speech data for each
speaker, including word count, time period, and the transcription of their speech.

The `get_speaker_speech_data` function retrieves and processes the speaker
segments and audio file, transcribing each segment and storing the data for
each speaker.
"""

from logger_config import get_logger

from .pydantic_models import (
    GetSpeakerSpeechDataInput,
    SpeakerSpeechData,
    SpeechData,
    TranscribeAudioSegmentInput,
)
from .transcription import transcribe_audio_segment

logger = get_logger()

def get_speaker_speech_data(data: GetSpeakerSpeechDataInput) -> SpeakerSpeechData:
    """Process speaker segments and transcribe speech data for each speaker.

    This function transcribes each speaker's segment, calculates the total
    word count, and computes the time duration for each speaker. The results
    are aggregated and returned as structured speech data.

    :param data: Contains speaker segments and audio file path to process.
    :type data: GetSpeakerSpeechDataInput
    :return: A collection of speech data for each speaker, including word
             count, time duration, and transcribed speech.
    :rtype: SpeakerSpeechData
    """
    speaker_segments = data.speaker_segments
    audio_path = data.audio_file
    speaker_speech_data = {}

    logger.info("Starting speaker speech data processing for file: %s", audio_path)

    for seg in speaker_segments:

        logger.info("Processing segment: speaker=%s, start_time=%.2f, end_time=%.2f",
                    seg.speaker, seg.start_time, seg.end_time)

        try:
            transcript_input = TranscribeAudioSegmentInput(
                audio_file=audio_path, start_time=seg.start_time, end_time=seg.end_time,
            )
            transcript = transcribe_audio_segment(transcript_input).transcription
            word_count = len(transcript.split())
            logger.info("Transcription successful for speaker %s: %d words",
            seg.speaker, word_count)
        except Exception:
            logger.exception("Error transcribing segment for speaker %s", seg.speaker)
            continue

        # Store words spoken and duration
        if seg.speaker not in speaker_speech_data:
            speaker_speech_data[seg.speaker] = SpeechData(
                length=word_count,
                time_period=seg.end_time - seg.start_time,
                speech=transcript,
            )
            logger.info("Created new speech data entry for speaker: %s", seg.speaker)
        else:
            speaker_speech_data[seg.speaker].length += word_count
            speaker_speech_data[seg.speaker].time_period+= seg.end_time - seg.start_time
            speaker_speech_data[seg.speaker].speech += " " + transcript
            logger.info("Updated speech data for speaker: %s", seg.speaker)

    logger.info("Completed processing of speaker speech data for file: %s", audio_path)
    return SpeakerSpeechData(speaker_speech_data=speaker_speech_data)
