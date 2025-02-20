from call_processor_modules.pydantic_models import CheckPIIInput, CheckPIIOutput
from . import pii_patterns, sensitive_words
import re

def check_pii(data: CheckPIIInput) -> CheckPIIOutput:
    text = data.transcribed_text
    detected = False
    masked_text = text

    for key, pattern in pii_patterns.items():
        if re.search(pattern, text):
            detected = True
            masked_text = re.sub(pattern, "****", masked_text)

    for word in sensitive_words:
        if word.lower() in text.lower():
            detected = True

    return CheckPIIOutput(detected=detected, masked_text=masked_text)
