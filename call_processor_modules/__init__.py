import yaml
import whisper
from better_profanity import profanity

# Load the YAML configuration file
with open('call_processor_modules/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize components
model = whisper.load_model(config['whisper_model'])
profanity_filter = profanity
pii_patterns = config['pii_patterns']
sensitive_words = config['sensitive_words']
categories = config['categories']
required_phrases = config['required_phrases']