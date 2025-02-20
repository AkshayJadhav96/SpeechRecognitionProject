from call_processor_modules.pydantic_models import CheckPIIInput, CheckPIIOutput
from . import pii_patterns, sensitive_words
import re


from logger_config import get_logger

logger = get_logger()

def check_pii(data: CheckPIIInput) -> CheckPIIOutput:
    """
    Checks for PII (Personally Identifiable Information) in the transcribed text.

    :param data: CheckPIIInput containing transcribed text.
    :return: CheckPIIOutput with detection flag and masked text.
    """
    try:
        text = data.transcribed_text
        detected = False
        masked_text = text

        logger.info("Starting PII detection.")

        for key, pattern in pii_patterns.items():
            if re.search(pattern, text):
                detected = True
                masked_text = re.sub(pattern, "****", masked_text)
                logger.warning(f"Detected possible {key} in text, masking it.")

        for word in sensitive_words:
            if word.lower() in text.lower():
                detected = True
                logger.warning(f"Sensitive word detected: {word}")

        if detected:
            logger.info("PII detected and masked.")
        else:
            logger.info("No PII detected in the transcribed text.")

        return CheckPIIOutput(detected=detected, masked_text=masked_text)

    except Exception as e:
        logger.exception("Error in PII detection")
        return CheckPIIOutput(detected=False, masked_text="0")
