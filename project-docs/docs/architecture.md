# Project Architecture  

This document describes the architecture of the **Customer Service Assistant** system.  

## Overview  

The system is designed to process real-time customer service calls, transcribe them into text, check for compliance, mask sensitive information, analyze sentiment, and evaluate speaking patterns. The system is modular, with each component focused on a specific task to ensure scalability and maintainability.

---

## System Workflow  

The following diagram illustrates the flow of data from audio input to the final report:

```mermaid
graph TD;
    A[Audio Input] -->|Speaker Diarization| B[Speaker Separation];
    B -->|Speech-to-Text| C[Transcription];

    C -->|Compliance & Prohibited Phrase Check| D[Compliance Check];
    C -->|PII Masking & Profanity Filtering| E[Secure Processing];
    C -->|Sentiment & Emotion Analysis| F[Sentiment Analysis];
    C -->|Speaking Speed & Interruptions| G[Speech Analytics];

    D -->|Compliance Report| H[Final Report];
    E -->|Masked & Processed Text| H;
    F -->|Emotion Insights| H;
    G -->|Speaker Insights| H;
```