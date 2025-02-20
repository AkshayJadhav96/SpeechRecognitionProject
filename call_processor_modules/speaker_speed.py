from call_processor_modules.pydantic_models import CalculateSpeakingSpeedInput, CalculateSpeakingSpeedOutput,TranscribeAudioSegmentInput
from .transcription import transcribe_audio_segment

def calculate_speaking_speed(data: CalculateSpeakingSpeedInput) -> CalculateSpeakingSpeedOutput:
    speaker_segments = data.speaker_segments
    audio_path = data.audio_file
    speaker_speech_data = {}

    for seg in speaker_segments:
        transcript_input = TranscribeAudioSegmentInput(audio_file=audio_path,start_time=seg.start_time,end_time=seg.end_time)
        transcript = transcribe_audio_segment(transcript_input).transcription
        if seg.speaker not in speaker_speech_data:
            speaker_speech_data[seg.speaker] = [len(transcript.split()), seg.end_time - seg.start_time]
        else:
            speaker_speech_data[seg.speaker][0] += len(transcript.split())
            speaker_speech_data[seg.speaker][1] += seg.end_time - seg.start_time

    speaking_speeds = {speaker: (data[0] / data[1]) * 60 for speaker, data in speaker_speech_data.items()}

    return CalculateSpeakingSpeedOutput(speaking_speeds=speaking_speeds)
