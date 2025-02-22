from call_processor_modules.pydantic_models import CalculateSpeakingSpeedOutput,SpeakerSpeechData
from .transcription import transcribe_audio_segment

from logger_config import get_logger

logger = get_logger()

def calculate_speaking_speed(input_speech_data: SpeakerSpeechData) -> CalculateSpeakingSpeedOutput:
    """
    Calculates the speaking speed (words per minute) for each speaker in the conversation.

    :param data: Contains speaker segments and audio file path.
    :return: Speaking speeds in words per minute for each speaker.
    """
    # try:
    #     logger.info(f"Starting speaking speed calculation for file: {data.audio_file}")

        # speaker_segments = data.speaker_segments
        # audio_path = data.audio_file
        # speaker_speech_data = {}

        # for seg in speaker_segments:
        #     try:
        #         logger.info(f"Processing segment for Speaker {seg.speaker}: {seg.start_time}s - {seg.end_time}s")

        #         # Transcribe the segment
        #         transcript_input = TranscribeAudioSegmentInput(
        #             audio_file=audio_path, start_time=seg.start_time, end_time=seg.end_time
        #         )
        #         transcript = transcribe_audio_segment(transcript_input).transcription
        #         word_count = len(transcript.split())

        #         logger.info(f"Speaker {seg.speaker}: {word_count} words spoken in {seg.end_time - seg.start_time} seconds")

        #         # Store words spoken and duration
        #         if seg.speaker not in speaker_speech_data:
        #             speaker_speech_data[seg.speaker] = [word_count, seg.end_time - seg.start_time]
        #         else:
        #             speaker_speech_data[seg.speaker][0] += word_count
        #             speaker_speech_data[seg.speaker][1] += seg.end_time - seg.start_time

        #     except Exception as e:
        #         logger.exception(f"Error processing segment for Speaker {seg.speaker}")

        # Calculate Words Per Minute (WPM)
    speaker_speech_data = input_speech_data.speaker_speech_data
    speaking_speeds = {
        speaker: (data.length / data.time_period) * 60 if data.time_period > 0 else 0
        for speaker, data in speaker_speech_data.items()
    }

    logger.info(f"Calculated Speaking Speeds: {speaking_speeds}")

    return CalculateSpeakingSpeedOutput(speaking_speeds=speaking_speeds)

    # except Exception as e:
    #     logger.exception("Error in calculate_speaking_speed")
    #     return CalculateSpeakingSpeedOutput(speaking_speeds={})
