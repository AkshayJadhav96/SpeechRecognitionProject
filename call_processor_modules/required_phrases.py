from . import required_phrases
import re

def check_required_phrases(transcribed_text):
    """
    Checks if required phrases are present in the transcribed text
    """
    present_phrases = [
        phrase
        for phrase in required_phrases
        if re.search(phrase, transcribed_text, re.IGNORECASE)
    ]
    if not present_phrases:
        # print("No required phrases present.")
        return False
    else:
        # print("Following Required phrases are present:")
        # for phrase in present_phrases:
        #     print(f"- {phrase}")
        return True