"""Pydantic Models for Customer Service Assistant.

This module defines the data models used in various components of
the customer service assistant system. These models ensure structured
data validation and serialization for functions related to speech
processing, categorization, sentiment analysis, PII detection,
profanity filtering, speaker diarization, and transcription.

Features:
- Defines structured input/output models for different functionalities.
- Uses Pydantic's `BaseModel` for validation and serialization.
- Provides well-typed attributes for accurate data handling.

Usage:
    Import the relevant model based on the function being called.

Example:
    ```python
    from models import CategorizeInput, CategorizeOutput
    ```

"""

from pydantic import BaseModel


# Model for `categorize` function
class CategorizeInput(BaseModel):
    """Input model for categorizing transcribed text."""

    transcribed_text: str

class CategorizeOutput(BaseModel):
    """Output model containing the detected category."""

    category: str

# Model for `check_pii` function
class CheckPIIInput(BaseModel):
    """Input model for detecting Personally Identifiable Information (PII)."""

    transcribed_text: str

class CheckPIIOutput(BaseModel):
    """Output model indicating PII detection and masked text."""

    detected: bool
    masked_text: str

# Model for `check_profanity` function
class CheckProfanityInput(BaseModel):
    """Input model for detecting profanity in transcribed text."""

    transcribed_text: str

class CheckProfanityOutput(BaseModel):
    """Output model indicating whether profanity was detected and censored text."""

    detected: bool
    censored_text: str

# Model for `check_required_phrases`
class CheckRequiredPhrasesInput(BaseModel):
    """Input model for checking the presence of required phrases in text."""

    transcribed_text: str

class CheckRequiredPhrasesOutput(BaseModel):
    """Output model indicating presence of required phrases and listing them."""

    required_phrases_present: bool
    present_phrases: list[str]

# Model for `analyse_sentiment`
class AnalyseSentimentInput(BaseModel):
    """Input model for sentiment analysis of transcribed text."""

    transcribed_text: str

class AnalyseSentimentOutput(BaseModel):
    """Output model containing polarity, subjectivity, and overall sentiment."""

    polarity: float
    subjectivity: float
    overall_sentiment: str

# Model for `diarize`
class DiarizeInput(BaseModel):
    """Input model for speaker diarization from an audio file."""

    audio_file: str

class SpeakerSegment(BaseModel):
    """Model representing a single speaker segment in an audio file."""

    speaker: str
    start_time: float
    end_time: float

class DiarizeOutput(BaseModel):
    """Output model containing speaker segmentation data and insights."""

    speaker_segments: list[SpeakerSegment]
    speaking_ratio: float | str
    interruptions: int
    time_to_first_token: float

# Model for `transcribe_audio_segment`
class TranscribeAudioSegmentInput(BaseModel):
    """Input model for transcribing a specific segment of an audio file."""

    audio_file: str
    start_time: float | None = None
    end_time: float | None = None

class TranscribeAudioSegmentOutput(BaseModel):
    """Output model containing the transcribed text from an audio segment."""

    transcription: str

# Model for 'get_speaker_speech_data'
class GetSpeakerSpeechDataInput(BaseModel):
    """Input model for retrieving speech data for different speakers."""

    speaker_segments: list[SpeakerSegment]
    audio_file: str

class SpeechData(BaseModel):
    """Model representing the details of a speech segment."""

    length: int
    time_period: float
    speech: str

class SpeakerSpeechData(BaseModel):
    """Output model containing speaker-wise speech data."""

    speaker_speech_data: dict[str, SpeechData]

class CalculateSpeakingSpeedOutput(BaseModel):
    """Output model containing calculated speaking speeds per speaker."""

    speaking_speeds: dict[str, float]
