from call_processor_modules.pydantic_models import CheckRequiredPhrasesInput, CheckRequiredPhrasesOutput
from . import required_phrases
import re

def check_required_phrases(data: CheckRequiredPhrasesInput) -> CheckRequiredPhrasesOutput:
    transcribed_text = data.transcribed_text
    present_phrases = [
        phrase
        for phrase in required_phrases
        if re.search(phrase, transcribed_text, re.IGNORECASE)
    ]
    return CheckRequiredPhrasesOutput(
        required_phrases_present=bool(present_phrases),
        present_phrases=present_phrases
    )
