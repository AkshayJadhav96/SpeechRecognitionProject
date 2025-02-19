from . import pii_patterns,sensitive_words
import re

def check_pii(text):
    """
    Checks for PII (Personally Identifiable Information) in the text
    """
    detected = False
    masked_text = text
    for key, pattern in pii_patterns.items():
        if re.search(pattern, text):
            # print(f"Warning: Possible {key} Detected")
            detected = True
            masked_text = re.sub(pattern, "****", masked_text)

    for word in sensitive_words:
        if word.lower() in text.lower():
            # print(f"Warning: Detected sensitive word - {word}")
            detected = True

    return detected, masked_text