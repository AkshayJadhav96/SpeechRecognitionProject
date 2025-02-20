# models.py
from pydantic import BaseModel
from typing import List, Dict, Tuple, Union, Optional

# Model for `categorize` function
class CategorizeInput(BaseModel):
    transcribed_text: str

class CategorizeOutput(BaseModel):
    category: str

# Model for `check_pii` function
class CheckPIIInput(BaseModel):
    transcribed_text: str

class CheckPIIOutput(BaseModel):
    detected: bool
    masked_text: str

# Model for `check_profanity` function
class CheckProfanityInput(BaseModel):
    transcribed_text: str

class CheckProfanityOutput(BaseModel):
    detected: bool
    censored_text: str

# Model for `check_required_phrases`
class CheckRequiredPhrasesInput(BaseModel):
    transcribed_text: str

class CheckRequiredPhrasesOutput(BaseModel):
    required_phrases_present: bool
    present_phrases: List[str]

# Model for `analyse_sentiment`
class AnalyseSentimentInput(BaseModel):
    transcribed_text: str

class AnalyseSentimentOutput(BaseModel):
    polarity: float
    subjectivity: float

# Model for `diarize`
class DiarizeInput(BaseModel):
    audio_file: str

class SpeakerSegment(BaseModel):
    speaker: str
    start_time: float
    end_time: float

class DiarizeOutput(BaseModel):
    speaker_segments: List[SpeakerSegment]
    speaking_ratio: Union[float, str]
    interruptions: int
    time_to_first_token: float

# Model for `calculate_speaking_speed`
class CalculateSpeakingSpeedInput(BaseModel):
    speaker_segments: List[SpeakerSegment]
    audio_file: str

class CalculateSpeakingSpeedOutput(BaseModel):
    speaking_speeds: Dict[str, float]

# Model for `transcribe_audio_segment`
class TranscribeAudioSegmentInput(BaseModel):
    audio_file: str
    start_time: Union[float, None] = None
    end_time: Union[float, None] = None

class TranscribeAudioSegmentOutput(BaseModel):
    transcription: str
