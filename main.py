import speech_recognition as sr
from better_profanity import profanity
from textblob import TextBlob
from pyannote.audio import Pipeline
import torch
import re
import os

class CallProcessor:
    """
    This class processes a call transcription and performs various checks
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.required_phrases = [
            "hello",
            "welcome",
            "thank you for calling",
            "this call is being recorded",
            "is there anything else I can help you with",
        ]
        self.profanity_filter = profanity  # Assuming profanity_filter is installed
        self.pii_patterns = {
            "Credit Card": r'\b(?:\d[ -]*?){13,16}\b',
            "ATM PIN": r'\b\d{4,6}\b',
            "Email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "Phone Number": r'\b\d{10}\b',
        }
        self.sensitive_words = ["password", "atm pin", "credit card","pin","atm"]

        # Defining categories with association keywords
        self.categories = {
            "Billing Issues": ["billing","invoice","charge","payment","refund","overcharge","undercharge","statement","fee","transaction","subscription","dues","penalty","late fee","dispute","incorrect charge","unbilled","outstanding balance","due date","autopay","failed payment","processing fee","chargeback","cancellation fee","hidden fees","credit","debit","account balance","payment declined","receipt","service charge","bill", "charge","exchange","discount"],
            "Technical Support": ["troubleshoot","error message","not working","unable to connect","crash","bug","fix issue","resolve problem","support ticket","customer support","it support","help desk","diagnose","configuration issue","compatibility issue","server down","network issue","latency","slow performance","software update","firmware update","patch","malfunction","system failure","blue screen","restart required","connection lost","authentication failed","access denied","data recovery","password reset","account locked","security breach","firewall issue","proxy error","hardware failure","device not recognized","driver update","installation failed","setup issue","runtime error"],
            "Account Management": ["account access", "login issue", "password reset", "update profile", "change email", "change phone number", "account locked", "verify identity", "security question", "two-factor authentication", "deactivate account", "reactivate account", "account suspension", "account termination", "profile settings", "subscription management", "upgrade plan", "downgrade plan", "payment method update", "billing address update", "account recovery", "username change", "merge accounts", "linked accounts", "access permissions", "role management", "account verification", "unauthorized access", "privacy settings", "data deletion request", "terms of service", "account dashboard", "contact support"],
            "General Inquiry": ["information request", "general question", "how to", "guidelines", "terms and conditions", "policy details", "service information", "contact support", "customer service", "faq", "opening hours", "business hours", "pricing details", "availability", "product details", "service status", "order status", "tracking information", "help needed", "assistance required", "directions", "company details", "support channels", "customer feedback", "user manual", "documentation", "report issue", "suggestion", "feature request", "about us", "contact details", "partnership inquiry", "collaboration request"],
            "Cancellation Requests": ["cancel subscription", "cancel order", "membership cancellation", "terminate account", "end service", "stop subscription", "discontinue plan", "request cancellation", "close account", "refund request", "cancellation policy", "early termination", "unsubscribe", "remove service", "void transaction", "delete account", "stop auto-renewal", "cancellation fee", "reverse charge", "withdraw request", "halt service", "stop payment", "cancel booking", "reschedule request", "terminate contract", "cease membership", "opt-out", "service discontinuation", "cancel trial", "deactivate service"],
            "Complaints": ["customer complaint", "file a complaint", "report issue", "bad experience", "poor service", "unsatisfactory response", "not happy", "frustrated", "disappointed", "service failure", "delayed response", "rude behavior", "unresolved issue", "poor quality", "defective product", "damaged item", "incorrect charge", "billing dispute", "refund problem", "scam", "fraud", "unauthorized transaction", "breach of policy", "misleading information", "false advertising", "late delivery", "missing item", "technical glitch", "login problem", "account hacked", "no response", "long wait time", "compensation request", "escalate issue"],
        }

    def call_to_text(self):
        """
        Performs speech recognition and returns the transcribed text
        """
        with sr.Microphone() as source:
            # self.recognizer.adjust_for_ambient_noise(source)
            print("Talk")
            audio_text = self.recognizer.listen(source)
            print("Time over, thanks")
            try:
                text = self.recognizer.recognize_google(audio_text)
                print("Text: " + text)
                return text
            except:
                print("Sorry, I did not get that")
                return None

    def check_required_phrases(self, transcribed_text):
        """
        Checks if required phrases are present in the transcribed text
        """
        present_phrases = [
            phrase
            for phrase in self.required_phrases
            if re.search(phrase, transcribed_text, re.IGNORECASE)
        ]
        if not present_phrases:
            print("No required phrases present.")
            return False
        else:
            print("Following Required phrases are present:")
            for phrase in present_phrases:
                print(f"- {phrase}")
            return True

    def Categorize(self, transcribed_text):
        detected_categories = {}

        for category, keywords in self.categories.items():
            count = sum(1 for keyword in keywords if re.search(r'\b' + keyword + r'\b', transcribed_text, re.IGNORECASE))
            if count > 0:
                detected_categories[category] = detected_categories.get(category, 0) + count  
        print(detected_categories)

        cat = "Unknown"
        mx = 0
        if detected_categories:
            for k, v in detected_categories.items():
                if v > mx:
                    mx = v  
                    cat = k  
            
            print("Call Category:", cat)
            return cat
        else:
            print("Call Category: Unknown")
            return cat

    def check_profanity(self, text):
        """
        Checks for profanity in the text and returns censored text
        """
        self.profanity_filter.load_censor_words()
        censored_text = self.profanity_filter.censor(text)
        if "*" in censored_text:
            print("Profanity detected in the text.")
            return True, censored_text
        else:
            print("No profanity detected.")
            return False, text

    def check_pii(self, text):
        """
        Checks for PII (Personally Identifiable Information) in the text
        """
        detected = False
        masked_text = text
        for key, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                print(f"Warning: Possible {key} Detected")
                detected = True
                masked_text = re.sub(pattern, "****", masked_text)

        for word in self.sensitive_words:
            if word.lower() in text.lower():
                print(f"Warning: Detected sensitive word - {word}")
                detected = True

        return detected, masked_text

    def sentiment_analysis(self, text):
        """
        Perform sentiment analysis on the transcribed text.
        Returns polarity and subjectivity scores.
        """
        # Analyze sentiment using TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Range: [-1, 1], where -1 is negative, 1 is positive
        subjectivity = blob.sentiment.subjectivity  # Range: [0, 1], where 0 is objective, 1 is subjective

        # Print results
        print("\nSentiment Analysis Results:")
        print(f"- Polarity: {polarity:.2f} (Negative to Positive)")
        print(f"- Subjectivity: {subjectivity:.2f} (Objective to Subjective)")

        # Interpret polarity
        if polarity > 0:
            print("  Overall Sentiment: Positive")
        elif polarity < 0:
            print("  Overall Sentiment: Negative")
        else:
            print("  Overall Sentiment: Neutral")

        return polarity, subjectivity

    def speaker_diarization(self, audio_file):
        """
        Performs speaker diarization using GPU if available and extracts:
        a) Customer-to-agent speaking ratio
        b) Agent interruptions count
        c) Time to first token (TTFT)
        """
        # Load the pre-trained speaker diarization pipeline
        # Load the pre-trained speaker diarization pipeline
        token = os.getenv("HUGGING_FACE_TOKEN")
        if not token:
            raise ValueError("Hugging Face token not found in environment variables.")

        # Use the token in your code
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)

        # Move pipeline to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        pipeline.to(device)

        # Apply the pipeline to the audio file
        diarization = pipeline(audio_file)

        # Store speaker segments
        speaker_segments = []
        print("\nSpeaker Diarization Results:")
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            print(f"- Speaker {speaker} spoke from {turn.start:.1f}s to {turn.end:.1f}s")
            speaker_segments.append((turn.start, turn.end, speaker))

        # Sort segments by start time
        speaker_segments.sort()

        # Compute metrics
        total_time = {}
        interruptions = 0
        first_speaker_time = None
        prev_speaker = None
        prev_end_time = 0

        for start, end, speaker in speaker_segments:
            duration = end - start
            total_time[speaker] = total_time.get(speaker, 0) + duration

            # Check for interruptions
            if prev_speaker and prev_speaker != speaker and start < prev_end_time:
                interruptions += 1

            # Capture first speaker's start time
            if first_speaker_time is None:
                first_speaker_time = start

            prev_speaker = speaker
            prev_end_time = end

        # Compute speaking ratio
        if len(total_time) >= 2:
            speakers = list(total_time.keys())
            ratio = total_time[speakers[0]] / total_time[speakers[1]]
        else:
            ratio = "N/A (only one speaker detected)"

        # Print analysis results
        print("\nAnalysis Results:")
        print(f"Customer-to-Agent Speaking Ratio: {ratio:.2f}" if isinstance(ratio, float) else ratio)
        print(f"Agent Interruptions: {interruptions}")
        print(f"Time to First Token (TTFT): {first_speaker_time:.2f}s")

        return diarization

    def process_call(self):
        """
        Calls the speech recognition, performs all checks, and prints results
        """
        transcribed_text = self.call_to_text()

        if transcribed_text:
            # Check for required phrases
            phrases_ok = self.check_required_phrases(transcribed_text)
            print(phrases_ok)

            #categorize the call
            category=self.Categorize(transcribed_text)
            print(category)

            # Check for profanity
            profanity_detected, clean_text = self.check_profanity(transcribed_text)
            print(clean_text)

            # Check for PII
            pii_detected, masked_text = self.check_pii(clean_text)
            print(masked_text)

            if pii_detected:
                print("Processed Text with Masked PII:")
                print(masked_text)
            
            # Perform sentiment analysis
            polarity, subjectivity = self.sentiment_analysis(masked_text)

            # Perform speaker diarization (requires an audio file)
            audio_file = "/home/aditya/Downloads/ElonMuskShort.wav"  # Replace with the actual path to the audio file
            diarization = self.speaker_diarization(audio_file)


# Example usage
cp = CallProcessor()

cp.process_call()