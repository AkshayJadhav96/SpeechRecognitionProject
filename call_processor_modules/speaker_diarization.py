from call_processor_modules.pydantic_models import DiarizeInput, DiarizeOutput, SpeakerSegment
from pyannote.audio import Pipeline
import torch
import os

from logger_config import get_logger

logger = get_logger()

def diarize(data: DiarizeInput) -> DiarizeOutput:

    try:
        audio_file = data.audio_file
        logger.info(f"Starting speaker diarization for file: {audio_file}")
        
        token = os.getenv("HUGGING_FACE_TOKEN")
        if not token:
            raise ValueError("Hugging Face token not found in environment variables.")
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        pipeline.to(device)
        logger.info(f"Pipeline loaded and moved to {device}")

        diarization = pipeline(audio_file)
        speaker_segments = []

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append(SpeakerSegment(
                speaker=speaker,
                start_time=turn.start,
                end_time=turn.end
            ))
        
        logger.info(f"Identified {len(speaker_segments)} speaker segments")

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

        if len(total_time) >= 2:
            speakers = list(total_time.keys())
            speaking_ratio = total_time[speakers[0]] / total_time[speakers[1]]
        else:
            speaking_ratio = "N/A (only one speaker detected)"
            # logger.warning("Only One Speaker Detected")

        logger.warning(f"Speaking ratio: {speaking_ratio}")
        logger.info(f"Interruptions count: {interruptions}")
        logger.info(f"Time to first token: {first_speaker_time or 0.0}")

        return DiarizeOutput(
            speaker_segments=speaker_segments,
            speaking_ratio=speaking_ratio,
            interruptions=interruptions,
            time_to_first_token=first_speaker_time or 0.0
        )
    
    except Exception as e:
        logger.exception(f"Error in speaker Diarization : {str(e)}")
        return DiarizeOutput(
            speaker_segments=[],
            speaking_ratio=speaking_ratio,
            interruptions=interruptions,
            time_to_first_token=first_speaker_time or 0.0
        )
        
    # speaker_segments: List[SpeakerSegment]
    # speaking_ratio: Union[float, str]
    # interruptions: int
    # time_to_first_token: float
