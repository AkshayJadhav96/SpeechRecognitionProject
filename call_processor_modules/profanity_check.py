from call_processor_modules.pydantic_models import CheckProfanityInput, CheckProfanityOutput
from . import profanity_filter

from logger_config import get_logger

logger = get_logger()

def check_profanity(data: CheckProfanityInput) -> CheckProfanityOutput:
    try:
        text = data.transcribed_text
        logger.info("Starting profanity check.")

        profanity_filter.load_censor_words()
        censored_text = profanity_filter.censor(text)

        if "*" in censored_text:
            logger.warning("Profanity detected in the text.")
            return CheckProfanityOutput(detected=True, censored_text=censored_text)
        else:
            logger.info("No profanity detected in the text.")
            return CheckProfanityOutput(detected=False, censored_text=text)

    except Exception as e:
        logger.exception("Error in profanity check")
        return CheckProfanityOutput(detected=False, censored_text="false")
