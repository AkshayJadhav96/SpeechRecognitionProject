from . import profanity_filter
def check_profanity(text):
        """
        Checks for profanity in the text and returns censored text
        """
        profanity_filter.load_censor_words()
        censored_text = profanity_filter.censor(text)
        if "*" in censored_text:
            # print("Profanity detected in the text.")
            return True, censored_text
        else:
            # print("No profanity detected.")
            return False, text
