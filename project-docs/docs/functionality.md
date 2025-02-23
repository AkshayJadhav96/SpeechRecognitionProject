# Functionality Overview

The **Customer Service Assistant** system processes customer service calls in real-time, providing functionalities such as speech-to-text conversion, speaker diarization, PII detection, sentiment analysis, and more.

## Key Functionalities  

### 1. **Speech-to-Text Conversion**
- **Description**: Converts spoken dialogue from the call into text for further processing.
- **How it works**:
    - The system uses **OpenAI Whisper** model for **speech-to-text transcription**.
    - This model provides high accuracy even in noisy environments.
    - The transcription is aligned with the identified speakers from the diarization module.
- **Key Features**:
    - Real-time transcription with high accuracy.
    - Handles multiple accents and noisy background environments effectively.

### 2. **Speaker Diarization**
- **Description**: Identifies and separates the speakers (customer vs. agent) in the conversation.
- **How it works**:
    - The system utilizes **Pyannote-audio** for speaker diarization.
    - The model detects when a speaker change occurs and assigns specific segments to the corresponding speakers (e.g., customer or agent).
- **Key Features**:
    - Real-time speaker identification.
    - Efficient separation of speaker segments for analysis.

### 3. **Compliance & Prohibited Phrase Check**
- **Description**: Ensures the conversation meets required compliance standards and checks for prohibited phrases.
- **How it works**:
    - The transcription is checked for mandatory compliance phrases like **greetings**, **disclaimers**, and **closing statements**.
- **Key Features**:
    - Identifies missing compliance phrases.

### 4. **PII Masking & Profanity Filtering**
- **Description**: Masks sensitive personal information (PII) and filters profanity from the transcript.
- **How it works**:
    - The system uses **regex patterns** to detect fixed sensitive words and personal information (e.g., names, phone numbers, addresses).
    - Profanity is filtered using the better_profanity module, which provides efficient detection and masking of inappropriate words.
- **Key Features**:
    - Real-time masking of PII using regex-based detection.
    - Profanity filtering without context alteration.

### 5. **Sentiment & Emotion Analysis**
- **Description**: Analyzes the sentiment and emotional tone of the conversation.
- **How it works**:
    - The system uses **TextBlob** to perform sentiment analysis and determine the emotional tone (positive, neutral, negative).
- **Key Features**:
    - Sentiment analysis for both speakers (customer and agent).
    - Emotion insights for deeper understanding of conversation dynamics.

### 6. **Speaking Speed & Interruptions Analysis**
- **Description**: Measures speaking speed and interruptions within the conversation.
- **How it works**:
    - The system calculates the **speaking speed** by dividing the total number of words spoken by each speaker by the total time they spoke.
    - It also detects **interruptions** (if one speaker speaks over the other).
- **Key Features**:
    - Calculates speaking speed in real-time for both speakers.
    - Detects interruptions and silence periods during conversations.

### 7. **Call Categorization**
- **Description**: Categorizes the conversation into predefined categories based on the transcript.
- **How it works**:
    - The system uses **regex** patterns to search for specific keywords and phrases within the transcript.
    - These keywords are mapped to categories like **billing**, **technical support**, **complaints**, etc.
- **Key Features**:
    - Automatically categorizes calls based on the conversation content.
    - Uses predefined categories for quick classification.

### 8. **Final Report Generation**
- **Description**: Aggregates all the insights (compliance, sentiment, speaking patterns) into a structured report.
- **How it works**:
    - The system consolidates all data into a **final categorized report**.
    - This report includes compliance scores, sentiment summaries, speaker insights, and any flags raised during the conversation.
- **Key Features**:
    - A comprehensive report with all key insights.
    - Categorizes calls based on predefined categories for easy reference.

---

## How to Run the Project

To run the **Customer Service Assistant**, follow these steps:

### **1. Setup the Environment**

Clone the repository and install the dependencies:

```bash
git clone https://github.com/your-repo/customer-service-assistant.git
cd customer-service-assistant
pip install -r requirements.txt
```