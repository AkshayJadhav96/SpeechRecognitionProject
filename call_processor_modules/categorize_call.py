"""Call Categorization Module.

This module provides functionality to categorize transcribed customer service
calls based on predefined keyword categories. It analyzes text using regex
pattern matching and assigns the most relevant category.

Features:
- Uses regex to identify keywords in predefined categories.
- Logs categorized results and any errors encountered.
- Returns the most probable category or "Unknown" if no match is found.

Dependencies:
    - `logger_config` for logging.
    - `pydantic_models` for structured input and output validation.

Usage:
    Pass a `CategorizeInput` object containing transcribed text,
    and receive a `CategorizeOutput` object with the detected category.
"""

import re

from logger_config import get_logger

from . import categories
from .pydantic_models import CategorizeInput, CategorizeOutput

logger = get_logger()

def categorize(data: CategorizeInput) -> CategorizeOutput:
    """Categorizes a transcribed text based on predefined categories.

    :param data: CategorizeInput containing transcribed text.
    :return: CategorizeOutput with the detected category.
    """
    try:
        transcribed_text = data.transcribed_text
        logger.info("Starting call categorization.")

        detected_categories = {}

        for category, keywords in categories.items():
            count = sum(1 for keyword in keywords if re.search(
            r"\b" + keyword + r"\b", transcribed_text, re.IGNORECASE))
            if count > 0:
                detected_categories[category] = detected_categories.get(
                category, 0) + count

        logger.info("Detected category counts: {detected_categories}")

        cat = "Unknown"
        mx = 0
        if detected_categories:
            for k, v in detected_categories.items():
                if v > mx:
                    mx = v
                    cat = k
            logger.info("Categorized call as: {cat}")
        else:
            logger.warning("No matching category found. Categorizing as 'Unknown'.")

        return CategorizeOutput(category=cat)

    except Exception:
        logger.exception("Error in call categorization")
        return CategorizeOutput(category="Unknown")
