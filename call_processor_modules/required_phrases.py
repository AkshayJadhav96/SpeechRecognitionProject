from call_processor_modules.pydantic_models import CheckRequiredPhrasesInput, CheckRequiredPhrasesOutput
from . import required_phrases
import re
from logger_config import get_logger

logger = get_logger()

def check_required_phrases(data: CheckRequiredPhrasesInput) -> CheckRequiredPhrasesOutput:
    """
    Checks if required phrases are present in the transcribed text.

    :param data: CheckRequiredPhrasesInput containing transcribed text.
    :return: CheckRequiredPhrasesOutput with a boolean flag and list of found phrases.
    """
    try:
        transcribed_text = data.transcribed_text
        logger.info("Starting required phrases check.")

        present_phrases = [
            phrase
            for phrase in required_phrases
            if re.search(phrase, transcribed_text, re.IGNORECASE)
        ]

        if present_phrases:
            logger.info(f"Required phrases found: {present_phrases}")
        else:
            logger.warning("No required phrases found in the transcribed text.")

        return CheckRequiredPhrasesOutput(
            required_phrases_present=bool(present_phrases),
            present_phrases=present_phrases
        )

    except Exception as e:
        logger.exception("Error in checking required phrases")
        return CheckRequiredPhrasesOutput(required_phrases_present=False, present_phrases=["0"])


