from pathlib import Path
from pydantic import ValidationError

from call_processor_modules.pydantic_models import TranscribeAudioSegmentInput,TranscribeAudioSegmentOutput,AnalyseSentimentInput,AnalyseSentimentOutput,CalculateSpeakingSpeedInput,CalculateSpeakingSpeedOutput,CategorizeInput,CategorizeOutput,CheckPIIInput,CheckPIIOutput,CheckRequiredPhrasesInput,CheckRequiredPhrasesOutput,DiarizeInput,DiarizeOutput,CheckProfanityInput,CheckProfanityOutput

from call_processor_modules.transcription import transcribe_audio_segment
from call_processor_modules.profanity_check import check_profanity
from call_processor_modules.required_phrases import check_required_phrases
from call_processor_modules.categorize_call import categorize
from call_processor_modules.pii_check import check_pii
from call_processor_modules.sentiment_analysis import analyse_sentiment
from call_processor_modules.speaker_diarization import diarize
from call_processor_modules.speaker_speed import calculate_speaking_speed

def main():
    try:
        # Step 1: Take the audio file path as input
        audio_file_path = input("Enter the path to the audio file: ")

        # Validate the audio file path using the Pydantic model
        audio_input = TranscribeAudioSegmentInput(audio_file=audio_file_path)
        audio_path = Path(audio_input.audio_file)

        if not audio_path.exists():
            print("Audio file not found. Please check the path and try again.")
            return

        # Step 2: Perform diarization
        print("\nPerforming speaker diarization...")
        diarization_input = DiarizeInput(audio_file=audio_input.audio_file)
        diarization_results = diarize(diarization_input)
        # print(diarization_results.interruptions)

        # Step 3: Transcribe the entire audio
        print("\nTranscribing the entire audio...")
        transcription_input = TranscribeAudioSegmentInput(audio_file=audio_input.audio_file)
        full_transcription = transcribe_audio_segment(transcription_input)

        # print("\nFull transcription:")
        # print(full_transcription.transcription)

        # Step 4: Check for PII
        print("\nChecking for PII...")
        pii_input = CheckPIIInput(transcribed_text=full_transcription.transcription)
        pii_output = check_pii(pii_input)
        print(f"PII present: {pii_output.detected}")
        print(f"Masked Text: {pii_output.masked_text}")

        # Step 5: Check for profanity
        print("\nChecking for profanity...")
        profanity_input = CheckProfanityInput(transcribed_text=full_transcription.transcription)
        profanity_output = check_profanity(profanity_input)
        print(f"Profanity present: {profanity_output.detected}")
        print(f"Censored Text: {profanity_output.censored_text}")

        # Step 6: Check for required phrases
        print("\nChecking for required phrases...")
        phrases_input = CheckRequiredPhrasesInput(transcribed_text=full_transcription.transcription)
        phrases_output = check_required_phrases(phrases_input)
        print(f"Required phrases present: {phrases_output.required_phrases_present}")

        # Step 7: Find the category of call
        print("\nFinding the category of the call...")
        categorize_input = CategorizeInput(transcribed_text=full_transcription.transcription)
        categorize_output = categorize(categorize_input)
        print(f"Required phrases present: {categorize_output.category}")
        

        # Step 8: Perform sentiment analysis
        print("\nPerforming sentiment analysis...")
        sentiment_input = AnalyseSentimentInput(transcribed_text=full_transcription.transcription)
        sentiment_output = analyse_sentiment(sentiment_input)
        print(f"Polarity: {sentiment_output.polarity:.2f} (Negative to Positive)")
        print(f"Subjectivity: {sentiment_output.subjectivity:.2f} (Objective to Subjective)")

        # Step 9: Calculate speaking speed for each speaker
        print("\nCalculating speaking speed for each speaker...")
        speaking_speed_input = CalculateSpeakingSpeedInput(
            speaker_segments = diarization_results.speaker_segments,
            audio_file=audio_input.audio_file
        )
        speaking_speeds = calculate_speaking_speed(speaking_speed_input)

        print("\nSpeaking Speed (Words Per Minute):")
        for speaker, speed in speaking_speeds.speaking_speeds.items():
            print(f"- Speaker {speaker}: {speed:.2f} WPM")

        print("\nAnalysis completed.")

    except ValidationError as e:
        print("Validation error occurred:")
        print(e.json())
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
