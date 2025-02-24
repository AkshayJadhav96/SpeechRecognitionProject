import asyncio
import json
import os
import shutil

# from logger_config import get_logger
# logger = get_logger()
import sys
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import individual modules
from call_processor_modules import (
    categorize_call,
    pii_check,
    profanity_check,
    sentiment_analysis,
    speaker_diarization,
    speaker_speed,
    transcription,
)
from call_processor_modules.required_phrases_check import (
    CheckRequiredPhrasesInput,
    check_required_phrases,
)
from call_processor_modules.speaker import (
    GetSpeakerSpeechDataInput,
    get_speaker_speech_data,
)

app = FastAPI()


class TranscriptionRequest(BaseModel):
    text: str


@app.post("/process_call/")
async def process_call(file: UploadFile = File(...), tasks: str = Form(...)):
    file_path = f"temp_{file.filename}"
    with Path.open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse the selected tasks
    selected_tasks = json.loads(tasks)

    # Process only the selected tasks
    async def process_call_step_by_step(file_path: str, selected_tasks: list):
        try:
            results = {}
            full_transcription = None
            diarization_results = None
            speaker_speech_data = None
            speed_results = None
            pii_results = None
            profanity_results = None
            phrases_results = None
            sentiment_results = None

            if "Transcription" in selected_tasks:
                try:
                    transcription_input = transcription.TranscribeAudioSegmentInput(
                    audio_file=file_path)
                    full_transcription = transcription.transcribe_audio_segment(
                    transcription_input)
                    results["transcription"] = full_transcription.transcription
                    yield f"data: {json.dumps({'step': 'transcription',
                    'result': results['transcription']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                    'result': f'Transcription failed: {e!s}'})}\n\n"

            if "Speaker Diarization" in selected_tasks:
                try:
                    diarization_input = speaker_diarization.DiarizeInput(
                    audio_file=file_path)
                    diarization_results = speaker_diarization.diarize(diarization_input)
                    results["diarization"] = {
                        "speaker_segments": [
                            {"start_time": segment.start_time,
                            "end_time": segment.end_time, "speaker": segment.speaker}
                            for segment in diarization_results.speaker_segments
                        ],
                        "speaking_ratio": diarization_results.speaking_ratio,
                        "interruptions": diarization_results.interruptions,
                        "time_to_first_token": diarization_results.time_to_first_token,
                    }
                    yield f"data: {json.dumps({'step': 'diarization',
                    'result': results['diarization']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                    'result': f'Diarization failed: {e!s}'})}\n\n"

            if "Speaking Speed" in selected_tasks and diarization_results:
                speech_data_input = GetSpeakerSpeechDataInput(
                    audio_file=file_path,
                    speaker_segments=diarization_results.speaker_segments,
                )
                speaker_speech_data = get_speaker_speech_data(speech_data_input)
                speed_results = speaker_speed.calculate_speaking_speed(
                speaker_speech_data)
                results["speaking_speed"] = speed_results.speaking_speeds
                yield f"data: {json.dumps({'step': 'speaking_speed',
                'result': results['speaking_speed']})}\n\n"
                await asyncio.sleep(1)

            if "PII Check" in selected_tasks and full_transcription:
                try:
                    pii_data_input = pii_check.CheckPIIInput(
                    transcribed_text=full_transcription.transcription)
                    pii_results = pii_check.check_pii(pii_data_input)
                    results["pii"] = {
                        "detected": pii_results.detected,
                        "masked_text": pii_results.masked_text,
                    }
                    yield f"data: {json.dumps({'step': 'pii',
                    'result': results['pii']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                    'result': f'PII check failed: {e!s}'})}\n\n"

            if "Profanity Check" in selected_tasks and full_transcription:
                try:
                    profanity_input_data = profanity_check.CheckProfanityInput(
                    transcribed_text=full_transcription.transcription)
                    profanity_results = profanity_check.check_profanity(
                    profanity_input_data)
                    results["profanity"] = {
                        "detected": profanity_results.detected,
                        "censored_text": profanity_results.censored_text,
                    }
                    yield f"data: {json.dumps({'step': 'profanity',
                    'result': results['profanity']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:

                    yield f"data: {json.dumps({'step': 'error',
                                'result': f'Profanity check failed: {e!s}'})}\n\n"

            if "Required Phrases" in selected_tasks and full_transcription:
                try:
                    phrases_input_data = CheckRequiredPhrasesInput(
                    transcribed_text=full_transcription.transcription)
                    phrases_results = check_required_phrases(phrases_input_data)
                    results["required_phrases"] = {
                        "required_phrases_present":
                        phrases_results.required_phrases_present,
                        "present_phrases": phrases_results.present_phrases,
                    }
                    yield f"data: {json.dumps({'step':
                    'required_phrases', 'result': results['required_phrases']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                    'result': f'Required phrases check failed: {e!s}'})}\n\n"

            if "Sentiment Analysis" in selected_tasks and full_transcription:
                try:
                    sentiment_input_data = sentiment_analysis.AnalyseSentimentInput(
                    transcribed_text=full_transcription.transcription)
                    sentiment_results = sentiment_analysis.analyse_sentiment(
                    sentiment_input_data)
                    results["sentiment"] = {
                        "polarity": sentiment_results.polarity,
                        "subjectivity": sentiment_results.subjectivity,
                        "overall_sentiment": sentiment_results.overall_sentiment,
                    }
                    yield f"data: {json.dumps({'step': 'sentiment',
                    'result': results['sentiment']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                    'result': f'Sentiment analysis failed: {e!s}'})}\n\n"

            if "Call Category" in selected_tasks and full_transcription:
                try:
                    category_input_data = categorize_call.CategorizeInput(
                    transcribed_text=full_transcription.transcription)
                    category_output = categorize_call.categorize(category_input_data)
                    results["category"] = {
                    "category": category_output.category}  # Extract attribute
                    yield f"data: {json.dumps(
                    {'step': 'category', 'result': results['category']})}\n\n"
                    await asyncio.sleep(1)
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error',
                     'result': f'Call categorization failed: {e!s}'})}\n\n"

            # Generate Summary Table
            # Generate Summary Table
            summary_table = {
                "columns": ["Analysis", "Speaker 1", "Speaker 2"],
                "rows": [],
            }

            # Extract speaker-specific data
            speaker_1_data = speaker_speech_data.speaker_speech_data.get(
            "SPEAKER_00", None)

            speaker_2_data = speaker_speech_data.speaker_speech_data.get(
            "SPEAKER_01", None)

            # Add Speech Data row
            summary_table["rows"].append([
                "Speech Data",
                f"Length: {speaker_1_data.length if speaker_1_data else 'N/A'}\nTime:{
                speaker_1_data.time_period if speaker_1_data else 'N/A'}",
                f"Length: {speaker_2_data.length if speaker_2_data else 'N/A'}\nTime:{
                speaker_2_data.time_period if speaker_2_data else 'N/A'}",
            ])

            # Add Speaking Speed row
            summary_table["rows"].append([
                "Speaking Speed (WPM)",
                f"{speed_results.speaking_speeds.get('SPEAKER_00', 'N/A')}",
                f"{speed_results.speaking_speeds.get('SPEAKER_01', 'N/A')}",
            ])

            # Add PII Check row
            pii_speaker_1 = pii_check.check_pii(pii_check.CheckPIIInput(
                transcribed_text=speaker_1_data.speech
                if speaker_1_data else "")) if speaker_1_data else None
            pii_speaker_2 = pii_check.check_pii(pii_check.CheckPIIInput(
                transcribed_text=speaker_2_data.speech
                if speaker_2_data else "")) if speaker_2_data else None
            summary_table["rows"].append([
                "PII Check",
                f"Detected: {pii_speaker_1.detected if pii_speaker_1 else 'N/A'}",
                f"Detected: {pii_speaker_2.detected if pii_speaker_2 else 'N/A'}",
            ])

            # Add Profanity Check row
            profanity_speaker_1 = profanity_check.check_profanity(
                profanity_check.CheckProfanityInput(
                transcribed_text=speaker_1_data.speech
                if speaker_1_data else "")) if speaker_1_data else None
            profanity_speaker_2 = profanity_check.check_profanity(
                profanity_check.CheckProfanityInput(
                transcribed_text=speaker_2_data.speech
                if speaker_2_data else "")) if speaker_2_data else None
            summary_table["rows"].append([
                "Profanity Check",
                f"Detected: {profanity_speaker_1.detected
                            if profanity_speaker_1 else 'N/A'}",
                f"Detected: {profanity_speaker_2.detected
                            if profanity_speaker_2 else 'N/A'}",
            ])

            # Add Required Phrases row
            phrases_speaker_1 = check_required_phrases(
            CheckRequiredPhrasesInput(
            transcribed_text=speaker_1_data.speech
            if speaker_1_data else ""))if speaker_1_data else None
            phrases_speaker_2 = check_required_phrases(
            CheckRequiredPhrasesInput(
            transcribed_text=speaker_2_data.speech
            if speaker_2_data else "")) if speaker_2_data else None
            required_phrases_speaker_1 = f"Present: {
            phrases_speaker_1.required_phrases_present}\nPhrases:{
            phrases_speaker_1.present_phrases
            if phrases_speaker_1 and phrases_speaker_1.required_phrases_present
            else 'N/A'}" if phrases_speaker_1 else "N/A"
            required_phrases_speaker_2 = f"Present: {
            phrases_speaker_2.required_phrases_present}\nPhrases:{
            phrases_speaker_2.present_phrases
            if phrases_speaker_2 and phrases_speaker_2.required_phrases_present
            else 'N/A'}" if phrases_speaker_2 else "N/A"
            summary_table["rows"].append([
                "Required Phrases",
                required_phrases_speaker_1,
                required_phrases_speaker_2,
            ])

            # Add Sentiment Analysis row
            sentiment_speaker_1 = sentiment_analysis.analyse_sentiment(
            sentiment_analysis.AnalyseSentimentInput(
            transcribed_text=speaker_1_data.speech
            if speaker_1_data else "")) if speaker_1_data else None
            sentiment_speaker_2 = sentiment_analysis.analyse_sentiment(
            sentiment_analysis.AnalyseSentimentInput(
            transcribed_text=speaker_2_data.speech
            if speaker_2_data else "")) if speaker_2_data else None
            summary_table["rows"].append([
                "Sentiment Analysis",
                f"Polarity: {sentiment_speaker_1.polarity
                             if sentiment_speaker_1 else 'N/A'}\nSubjectivity:{
                sentiment_speaker_1.subjectivity
                if sentiment_speaker_1 else 'N/A'}\nOverall:{
                sentiment_speaker_1.overall_sentiment
                if sentiment_speaker_1 else 'N/A'}",
                f"Polarity: {sentiment_speaker_2.polarity
                if sentiment_speaker_2 else 'N/A'}\nSubjectivity:{
                sentiment_speaker_2.subjectivity
                if sentiment_speaker_2 else 'N/A'}\nOverall:{
                sentiment_speaker_2.overall_sentiment
                if sentiment_speaker_2 else 'N/A'}",
            ])

            # Yield the summary table
            yield f"data: {json.dumps({'step': 'summary', 'result': summary_table})}\n"

            # Cleanup
            Path.unlink(file_path)
            yield f"data: {json.dumps({'step': 'complete',
                                       'result': 'Call processing completed.'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'result': str(e)})}\n\n"

    return StreamingResponse(process_call_step_by_step(
    file_path, selected_tasks), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)