from pydub import AudioSegment
from . import model

def transcribe_audio_segment(audio_file_path,start_time=None, end_time=None):    
    # Step 1: Load the audio file using pydub
    audio = AudioSegment.from_file(audio_file_path)
    
    # Step 2: Extract the segment (convert start_time and end_time to milliseconds)
    if start_time and end_time:
        segment = audio[start_time * 1000:end_time * 1000]  # pydub works with milliseconds
    else:
        segment = audio
    # Step 3: Save the segment as a temporary WAV file
    temp_wav_path = "temp_segment.wav"
    segment.export(temp_wav_path, format="wav")

    # Transcribe the temporary audio segment
    result = model.transcribe(temp_wav_path)

    # Remove the temporary file (optional, but good practice)
    import os
    os.remove(temp_wav_path)

    # Step 6: Recognize speech using Google's Speech-to-Text (or any other recognizer)
    try:
        # Use Google's speech recognition (or any other supported engine)
        transcription = result["text"]
        return transcription
    except Exception as e:
        return f"Could not perform transcription; {e}"