"""Speech Processing Module.

This module initializes components for processing customer service calls.
It loads configurations from a YAML file and sets up:
- Whisper ASR model for speech-to-text transcription.
- Profanity filtering using the `better_profanity` package.
- PII (Personally Identifiable Information) pattern detection.
- Sensitive word filtering and required phrase validation.

"""

from pathlib import Path

import whisper
import yaml
from better_profanity import profanity

# Load the YAML configuration file
config_path = Path("call_processor_modules/config.yaml")
with config_path.open() as file:
    config = yaml.safe_load(file)

# Initialize components
model = whisper.load_model(config["whisper_model"])
profanity_filter = profanity
pii_patterns = config["pii_patterns"]
sensitive_words = config["sensitive_words"]
categories = config["categories"]
required_phrases = config["required_phrases"]
