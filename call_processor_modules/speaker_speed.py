from .transcription import transcribe_audio_segment

def calculate_speaking_speed(speaker_segments,audio_path):
    speaker_speech_data = {}

    for seg in speaker_segments:
        speaker_transcript = transcribe_audio_segment(audio_path, seg[0],seg[1])
        if seg[-1] not in speaker_speech_data:
            speaker_speech_data[seg[-1]] = [len(speaker_transcript.split()),seg[1]-seg[0]]
        else:
            speaker_speech_data[seg[-1]][0] += len(speaker_transcript.split())
            speaker_speech_data[seg[-1]][1] += seg[1]-seg[0]
    
    # Calculate WPM (Words per Minute)
    speeds = {}
    for speaker in speaker_speech_data:
        speeds[speaker] = (speaker_speech_data[speaker][0]/speaker_speech_data[speaker][1])*60

    return speeds