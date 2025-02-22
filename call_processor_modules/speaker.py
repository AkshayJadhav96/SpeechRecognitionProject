from .transcription import transcribe_audio_segment
from .pydantic_models import TranscribeAudioSegmentInput,GetSpeakerSpeechDataInput,SpeakerSpeechData,SpeechData

def get_speaker_speech_data(data: GetSpeakerSpeechDataInput) -> SpeakerSpeechData: 
    speaker_segments = data.speaker_segments
    audio_path = data.audio_file
    speaker_speech_data = {}
    for seg in speaker_segments:
        # Transcribe the segment
        transcript_input = TranscribeAudioSegmentInput(
            audio_file=audio_path, start_time=seg.start_time, end_time=seg.end_time
        )
        transcript = transcribe_audio_segment(transcript_input).transcription
        word_count = len(transcript.split())

        # Store words spoken and duration
        if seg.speaker not in speaker_speech_data:
            # speaker_speech_data[seg.speaker] = [word_count, seg.end_time - seg.start_time,transcript]
            speaker_speech_data[seg.speaker] = SpeechData(length=word_count,time_period = seg.end_time - seg.start_time,speech = transcript)
        else:
            speaker_speech_data[seg.speaker].length += word_count
            speaker_speech_data[seg.speaker].time_period += seg.end_time - seg.start_time
            speaker_speech_data[seg.speaker].speech += transcript

    return SpeakerSpeechData(speaker_speech_data=speaker_speech_data)