"""Module: check_required_phrases.

This module provides functionality to check if specific required phrases
are present in a transcribed text. It helps ensure that mandatory phrases
(such as greetings, disclaimers, or acknowledgments) are included in
customer service interactions.

Features:
- Uses regex matching to detect required phrases in the transcribed text.
- Logs detected phrases or missing phrases for further analysis.
- Returns a structured response with found phrases.

Usage:
    ```python
    from check_required_phrases import check_required_phrases
    from call_processor_modules.pydantic_models import CheckRequiredPhrasesInput

    input_data = CheckRequiredPhrasesInput(
    transcribed_text="Hello, welcome to our service.")
    output = check_required_phrases(input_data)
    print(output)
    ```
"""

import re

from call_processor_modules.pydantic_models import (
    CheckRequiredPhrasesInput,
    CheckRequiredPhrasesOutput,
)
from logger_config import get_logger

from . import required_phrases

logger = get_logger()

def check_required_phrases(
    data: CheckRequiredPhrasesInput) -> CheckRequiredPhrasesOutput:
    """Check if required phrases are present in the transcribed text.

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
            logger.info("Required phrases found: {present_phrases}")
        else:
            logger.warning("No required phrases found in the transcribed text.")

        return CheckRequiredPhrasesOutput(
            required_phrases_present=bool(present_phrases),
            present_phrases=present_phrases,
        )

    except Exception:
        logger.exception("Error in checking required phrases")
        return CheckRequiredPhrasesOutput(
        required_phrases_present=False, present_phrases=["0"])


