from .pydantic_models import CategorizeInput, CategorizeOutput
from . import categories
import re

def categorize(data: CategorizeInput) -> CategorizeOutput:
    transcribed_text = data.transcribed_text
    detected_categories = {}

    for category, keywords in categories.items():
        count = sum(1 for keyword in keywords if re.search(r'\b' + keyword + r'\b', transcribed_text, re.IGNORECASE))
        if count > 0:
            detected_categories[category] = detected_categories.get(category, 0) + count  

    cat = "Unknown"
    mx = 0
    if detected_categories:
        for k, v in detected_categories.items():
            if v > mx:
                mx = v  
                cat = k  
        return CategorizeOutput(category=cat)
    else:
        return CategorizeOutput(category="Unknown")
