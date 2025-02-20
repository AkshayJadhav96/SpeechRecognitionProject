from call_processor_modules.pydantic_models import CheckProfanityInput, CheckProfanityOutput
from . import profanity_filter

def check_profanity(data: CheckProfanityInput) -> CheckProfanityOutput:
    text = data.transcribed_text
    profanity_filter.load_censor_words()
    censored_text = profanity_filter.censor(text)

    if "*" in censored_text:
        return CheckProfanityOutput(detected=True, censored_text=censored_text)
    else:
        return CheckProfanityOutput(detected=False, censored_text=text)
