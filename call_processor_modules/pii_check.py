"""PII Detection Module.

This module detects and masks Personally Identifiable Information (PII)
from transcribed text in customer service calls. It ensures compliance
by identifying sensitive patterns and replacing them with masked placeholders.

Features:
- Uses regex patterns to detect common PII (e.g., phone numbers, emails).
- Detects predefined sensitive words.
- Masks detected PII with '****' for privacy.
- Logs detected instances and warnings.

Dependencies:
    - `call_processor_modules.pydantic_models`
        for structured input and output validation.
    - `logger_config` for logging.

Usage:
    Pass a `CheckPIIInput` object containing transcribed text,
    and receive a `CheckPIIOutput` object with masked text and detection status.

"""

import re

from call_processor_modules.pydantic_models import CheckPIIInput, CheckPIIOutput
from logger_config import get_logger

from . import pii_patterns, sensitive_words

logger = get_logger()

def check_pii(data: CheckPIIInput) -> CheckPIIOutput:
    """Check for PII (Personally Identifiable Information) in the transcribed text.

    :param data: CheckPIIInput containing transcribed text.
    :return: CheckPIIOutput with detection flag and masked text.
    """
    try:
        text = data.transcribed_text
        detected = False
        masked_text = text

        logger.info("Starting PII detection.")

        for pattern in pii_patterns.values():
            if re.search(pattern, text):
                detected = True
                masked_text = re.sub(pattern, "****", masked_text)
                logger.warning("Detected possible {key} in text, masking it.")

        for word in sensitive_words:
            if word.lower() in text.lower():
                detected = True
                logger.warning("Sensitive word detected: {word}")

        if detected:
            logger.info("PII detected and masked.")
        else:
            logger.info("No PII detected in the transcribed text.")

        return CheckPIIOutput(detected=detected, masked_text=masked_text)

    except Exception:
        logger.exception("Error in PII detection")
        return CheckPIIOutput(detected=False, masked_text="0")
