"""Profanity Detection Module.

This module detects and censors profanity in transcribed customer service
calls to maintain professionalism and compliance with company policies.

Features:
- Uses a profanity filter to censor offensive words.
- Loads and applies a list of predefined censor words.
- Logs detected profanities and masks them in the output.

Dependencies:
    - `call_processor_modules.pydantic_models` for structured input
        and output validation.
    - `logger_config` for logging.
    - `profanity_filter` for filtering and censoring offensive words.

Usage:
    Pass a `CheckProfanityInput` object containing transcribed text,
    and receive a `CheckProfanityOutput` object with the censored text
    and a detection flag.

"""

from call_processor_modules.pydantic_models import (
    CheckProfanityInput,
    CheckProfanityOutput,
)
from logger_config import get_logger

from . import profanity_filter

logger = get_logger()

def check_profanity(data: CheckProfanityInput) -> CheckProfanityOutput:
    """Check for profanity in the transcribed text and censor offensive words.

    :param data: CheckProfanityInput containing transcribed text.
    :return: CheckProfanityOutput with detection flag and censored text.

    This function:
    - Loads a predefined list of profanity words.
    - Censors any detected offensive words in the input text.
    - Logs whether profanity was detected or not.
    """
    try:
        text = data.transcribed_text
        logger.info("Starting profanity check.")

        profanity_filter.load_censor_words()
        censored_text = profanity_filter.censor(text)

        if "*" in censored_text:
            logger.warning("Profanity detected in the text.")
            return CheckProfanityOutput(detected=True, censored_text=censored_text)
        logger.info("No profanity detected in the text.")
        return CheckProfanityOutput(detected=False, censored_text=text)

    except Exception:
        logger.exception("Error in profanity check")
        return CheckProfanityOutput(detected=False, censored_text="false")
