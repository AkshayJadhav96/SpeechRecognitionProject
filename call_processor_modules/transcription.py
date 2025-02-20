from call_processor_modules.pydantic_models import TranscribeAudioSegmentInput, TranscribeAudioSegmentOutput
from pydub import AudioSegment
from . import model

def transcribe_audio_segment(data: TranscribeAudioSegmentInput) -> TranscribeAudioSegmentOutput:
    audio = AudioSegment.from_file(data.audio_file)

    if data.start_time and data.end_time:
        segment = audio[data.start_time * 1000:data.end_time * 1000]
    else:
        segment = audio

    temp_wav_path = "temp_segment.wav"
    segment.export(temp_wav_path, format="wav")
    result = model.transcribe(temp_wav_path)

    import os
    os.remove(temp_wav_path)

    try:
        transcription = result["text"]
        return TranscribeAudioSegmentOutput(transcription=transcription)
    except Exception as e:
        return TranscribeAudioSegmentOutput(transcription=f"Could not perform transcription; {e}")
