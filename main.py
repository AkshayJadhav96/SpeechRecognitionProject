from pathlib import Path
from pydantic import ValidationError

from call_processor_modules.pydantic_models import TranscribeAudioSegmentInput,TranscribeAudioSegmentOutput,AnalyseSentimentInput,AnalyseSentimentOutput,CalculateSpeakingSpeedOutput,CategorizeInput,CategorizeOutput,CheckPIIInput,CheckPIIOutput,CheckRequiredPhrasesInput,CheckRequiredPhrasesOutput,DiarizeInput,DiarizeOutput,CheckProfanityInput,CheckProfanityOutput,GetSpeakerSpeechDataInput,SpeakerSpeechData,SpeechData

from call_processor_modules.transcription import transcribe_audio_segment
from call_processor_modules.profanity_check import check_profanity
from call_processor_modules.required_phrases import check_required_phrases
from call_processor_modules.categorize_call import categorize
from call_processor_modules.pii_check import check_pii
from call_processor_modules.sentiment_analysis import analyse_sentiment
from call_processor_modules.speaker_diarization import diarize
from call_processor_modules.speaker_speed import calculate_speaking_speed
from call_processor_modules.speaker import get_speaker_speech_data

from logger_config import get_logger

logger = get_logger()

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
        logger.info("diarization function done")
        # print(diarization_results.interruptions)

        # Step 3: Transcribe the entire audio
        print("\nTranscribing the entire audio...")
        transcription_input = TranscribeAudioSegmentInput(audio_file=audio_input.audio_file)
        full_transcription = transcribe_audio_segment(transcription_input)
        logger.info("transcription function done")

        # print("\nFull transcription:")
        # print(full_transcription.transcription)

        if full_transcription.transcription!="False":
            # Step 4: Check for PII
            print("\nChecking for PII...")
            pii_input = CheckPIIInput(transcribed_text=full_transcription.transcription)
            pii_output = check_pii(pii_input)
            if pii_output.masked_text=="0":
                logger.warning("error in PII detection")
            else:
                print(f"PII present: {pii_output.detected}")
                print(f"Masked Text: {pii_output.masked_text}")
                logger.info("PII check function done")

            # Step 5: Check for profanity
            print("\nChecking for profanity...")
            profanity_input = CheckProfanityInput(transcribed_text=full_transcription.transcription)
            profanity_output = check_profanity(profanity_input)
            if profanity_output.censored_text=="false":
                logger.warning("Error in Profanity Check")
            else:
                print(f"Profanity present: {profanity_output.detected}")
                print(f"Censored Text: {profanity_output.censored_text}")
                logger.info("Profanity function done")

            # Step 6: Check for required phrases
            print("\nChecking for required phrases...")
            phrases_input = CheckRequiredPhrasesInput(transcribed_text=full_transcription.transcription)
            phrases_output = check_required_phrases(phrases_input)
            if phrases_output.present_phrases==["0"]:
                logger.warning("Error in phrase detection")
            else:
                print(f"Required phrases present: {phrases_output.required_phrases_present}")
                logger.info("required phrase function done")

            # Step 7: Find the category of call
            print("\nFinding the category of the call...")
            categorize_input = CategorizeInput(transcribed_text=full_transcription.transcription)
            categorize_output = categorize(categorize_input)
            if (categorize_output.category=="UnKnown"):
                logger.warning("error in categorization of call")
            else:
                print(f"Required phrases present: {categorize_output.category}")
                logger.info("categorization fucntion done")

            # Step 8: Perform sentiment analysis
            print("\nPerforming sentiment analysis...")
            sentiment_input = AnalyseSentimentInput(transcribed_text=full_transcription.transcription)
            sentiment_output = analyse_sentiment(sentiment_input)
            if (sentiment_output.polarity==0.0 and sentiment_output.subjectivity==0.0):
                logger.warning("Error in Sentiment Analysis")
            else:
                print(f"Polarity: {sentiment_output.polarity:.2f} (Negative to Positive)")
                print(f"Subjectivity: {sentiment_output.subjectivity:.2f} (Objective to Subjective)")
                logger.info("sentiment analysis function done")

        else:
            logger.error("Transcription of call not successful")

        # Step 9: Calculate speaking speed for each speaker
        print("\nCalculating speaking speed for each speaker...")
        if diarization_results:
            data = GetSpeakerSpeechDataInput(speaker_segments = diarization_results.speaker_segments,
                audio_file=audio_input.audio_file)
            speaker_speed_input = get_speaker_speech_data(data=data)
            speaking_speeds = calculate_speaking_speed(speaker_speed_input).speaking_speeds
            if speaking_speeds!={}:
                print("\nSpeaking Speed (Words Per Minute):")
                for speaker, speed in speaking_speeds.items():
                    print(f"- Speaker {speaker}: {speed:.2f} WPM")
                logger.info("speed detection function done")
            else:
                logger.error("Error is speaking speed")
        else:
            logger.error("Cant detect speaking speed as no diarization results")


        print("\nAnalysis completed.")

    except:
        logger.error("Error Occured")

if __name__ == "__main__":
    main()
