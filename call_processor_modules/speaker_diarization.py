from pyannote.audio import Pipeline
import torch
import os

def diarize(audio_file):
    """
    Performs speaker diarization using GPU if available and extracts:
    a) Customer-to-agent speaking ratio
    b) Agent interruptions count
    c) Time to first token (TTFT)
    """
    # Load the pre-trained speaker diarization pipeline
    # Load the pre-trained speaker diarization pipeline
    
    # token = os.getenv("HUGGING_FACE_TOKEN")
    # if not token:
    #     raise ValueError("Hugging Face token not found in environment variables.")

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

    # Move pipeline to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)

    # Apply the pipeline to the audio file
    diarization = pipeline(audio_file)

    # Store speaker segments
    speaker_segments = []
    print("\nSpeaker Diarization Results:")
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"- Speaker {speaker} spoke from {turn.start:.1f}s to {turn.end:.1f}s")
        speaker_segments.append((turn.start, turn.end, speaker))

    # Sort segments by start time
    speaker_segments.sort()

    # Compute metrics
    total_time = {}
    interruptions = 0
    first_speaker_time = None
    prev_speaker = None
    prev_end_time = 0

    for start, end, speaker in speaker_segments:
        duration = end - start
        total_time[speaker] = total_time.get(speaker, 0) + duration

        # Check for interruptions
        if prev_speaker and prev_speaker != speaker and start < prev_end_time:
            interruptions += 1

        # Capture first speaker's start time
        if first_speaker_time is None:
            first_speaker_time = start

        prev_speaker = speaker
        prev_end_time = end

    # Compute speaking ratio
    if len(total_time) >= 2:
        speakers = list(total_time.keys())
        ratio = total_time[speakers[0]] / total_time[speakers[1]]
    else:
        ratio = "N/A (only one speaker detected)"

    # Print analysis results
    print("\nAnalysis Results:")
    print(f"Customer-to-Agent Speaking Ratio: {ratio:.2f}" if isinstance(ratio, float) else ratio)
    print(f"Agent Interruptions: {interruptions}")
    print(f"Time to First Token (TTFT): {first_speaker_time:.2f}s")

    return diarization,speaker_segments