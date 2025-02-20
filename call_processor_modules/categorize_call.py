from .pydantic_models import CategorizeInput, CategorizeOutput
from . import categories
import re

from logger_config import get_logger

logger = get_logger()

def categorize(data: CategorizeInput) -> CategorizeOutput:
    """
    Categorizes a transcribed text based on predefined categories.

    :param data: CategorizeInput containing transcribed text.
    :return: CategorizeOutput with the detected category.
    """
    try:
        transcribed_text = data.transcribed_text
        logger.info("Starting call categorization.")

        detected_categories = {}

        for category, keywords in categories.items():
            count = sum(1 for keyword in keywords if re.search(r'\b' + keyword + r'\b', transcribed_text, re.IGNORECASE))
            if count > 0:
                detected_categories[category] = detected_categories.get(category, 0) + count  

        logger.info(f"Detected category counts: {detected_categories}")

        cat = "Unknown"
        mx = 0
        if detected_categories:
            for k, v in detected_categories.items():
                if v > mx:
                    mx = v  
                    cat = k  
            logger.info(f"Categorized call as: {cat}")
        else:
            logger.warning("No matching category found. Categorizing as 'Unknown'.")

        return CategorizeOutput(category=cat)

    except Exception as e:
        logger.exception("Error in call categorization")
        return CategorizeOutput(category="Unknown")
