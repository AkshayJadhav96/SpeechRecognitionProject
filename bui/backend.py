"""Backend module for processing audio files and performing various analyses.

This module provides a FastAPI application that accepts an audio file and a
list of tasks
to perform on the file. The tasks include transcription, speaker diarization, speaking
speed analysis, PII check, profanity check, required phrases check, sentiment analysis,
and call categorization. The results are streamed back to the client in real-time.
"""

import asyncio
import json
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

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
    """Request model for transcription input."""

    text: str


@app.post("/process_call/")
async def process_call(
    file: Annotated[UploadFile, File(...)],
    tasks: Annotated[str, Form(...)],
) -> StreamingResponse:
    """Process an audio file and perform the selected tasks.

    Args:
        file: The uploaded audio file.
        tasks: A JSON string containing the list of tasks to perform.

    Returns:
        StreamingResponse: A streaming response with the results of the tasks.

    """
    file_path = f"temp_{file.filename}"
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(await file.read())

    # Parse the selected tasks
    selected_tasks = json.loads(tasks)

    return StreamingResponse(
        process_call_step_by_step(file_path, selected_tasks),
        media_type="text/event-stream",
    )


async def process_call_step_by_step(
    file_path: str, selected_tasks: list[str],
) -> AsyncGenerator[str, None]:
    """Process the audio file step by step and yield results.

    Args:
        file_path: Path to the audio file.
        selected_tasks: List of tasks to perform.

    Yields:
        str: JSON-encoded results for each step.

    """
    try:
        results: dict[str, str] = {}
        full_transcription = None
        diarization_results = None
        speaker_speech_data = None
        speed_results = None
        pii_results = None
        profanity_results = None
        phrases_results = None
        sentiment_results = None

        # Transcription
        transcription_input = transcription.TranscribeAudioSegmentInput(
            audio_file=file_path,
        )
        full_transcription = transcription.transcribe_audio_segment(transcription_input)

        if "Transcription" in selected_tasks:
            try:
                results["transcription"] = full_transcription.transcription
                yield _format_result("transcription", results["transcription"])
                await asyncio.sleep(1)
            except transcription.TranscriptionError as e:
                yield _format_error("Transcription failed", str(e))

        # Speaker Diarization
        if "Speaker Diarization" in selected_tasks:
            try:
                diarization_input=speaker_diarization.DiarizeInput(audio_file=file_path)
                diarization_results = speaker_diarization.diarize(diarization_input)
                results["diarization"] = {
                    "speaker_segments": [
                        {
                            "start_time": segment.start_time,
                            "end_time": segment.end_time,
                            "speaker": segment.speaker,
                        }
                        for segment in diarization_results.speaker_segments
                    ],
                    "speaking_ratio": diarization_results.speaking_ratio,
                    "interruptions": diarization_results.interruptions,
                    "time_to_first_token": diarization_results.time_to_first_token,
                }
                yield _format_result("diarization", results["diarization"])
                await asyncio.sleep(1)
            except speaker_diarization.DiarizationError as e:
                yield _format_error("Diarization failed", str(e))

        # Speaking Speed
        if "Speaking Speed" in selected_tasks and diarization_results:
            speech_data_input = GetSpeakerSpeechDataInput(
                audio_file=file_path,
                speaker_segments=diarization_results.speaker_segments,
            )
            speaker_speech_data = get_speaker_speech_data(speech_data_input)
            speed_results = speaker_speed.calculate_speaking_speed(speaker_speech_data)
            results["speaking_speed"] = speed_results.speaking_speeds
            yield _format_result("speaking_speed", results["speaking_speed"])
            await asyncio.sleep(1)

        # PII Check
        if "PII Check" in selected_tasks and full_transcription:
            try:
                pii_data_input = pii_check.CheckPIIInput(
                    transcribed_text=full_transcription.transcription,
                )
                pii_results = pii_check.check_pii(pii_data_input)
                results["pii"] = {
                    "detected": pii_results.detected,
                    "masked_text": pii_results.masked_text,
                }
                yield _format_result("pii", results["pii"])
                await asyncio.sleep(1)
            except pii_check.PIICheckError as e:
                yield _format_error("PII check failed", str(e))

        # Profanity Check
        if "Profanity Check" in selected_tasks and full_transcription:
            try:
                profanity_input_data = profanity_check.CheckProfanityInput(
                    transcribed_text=full_transcription.transcription,
                )
                profanity_results =profanity_check.check_profanity(profanity_input_data)
                results["profanity"] = {
                    "detected": profanity_results.detected,
                    "censored_text": profanity_results.censored_text,
                }
                yield _format_result("profanity", results["profanity"])
                await asyncio.sleep(1)
            except profanity_check.ProfanityCheckError as e:
                yield _format_error("Profanity check failed", str(e))

        # Required Phrases
        if "Required Phrases" in selected_tasks and full_transcription:
            try:
                phrases_input_data = CheckRequiredPhrasesInput(
                    transcribed_text=full_transcription.transcription,
                )
                phrases_results = check_required_phrases(phrases_input_data)
                results["required_phrases"] = {
                    "required_phrases_present":phrases_results.required_phrases_present,
                    "present_phrases": phrases_results.present_phrases,
                }
                yield _format_result("required_phrases", results["required_phrases"])
                await asyncio.sleep(1)
            except check_required_phrases.RequiredPhrasesError as e:
                yield _format_error("Required phrases check failed", str(e))

        # Sentiment Analysis
        if "Sentiment Analysis" in selected_tasks and full_transcription:
            try:
                sentiment_input_data = sentiment_analysis.AnalyseSentimentInput(
                    transcribed_text=full_transcription.transcription,
                )
                sentiment_results = sentiment_analysis.analyse_sentiment(
                    sentiment_input_data)
                results["sentiment"] = {
                    "polarity": sentiment_results.polarity,
                    "subjectivity": sentiment_results.subjectivity,
                    "overall_sentiment": sentiment_results.overall_sentiment,
                }
                yield _format_result("sentiment", results["sentiment"])
                await asyncio.sleep(1)
            except sentiment_analysis.SentimentAnalysisError as e:
                yield _format_error("Sentiment analysis failed", str(e))

        # Call Category
        if "Call Category" in selected_tasks and full_transcription:
            try:
                category_input_data = categorize_call.CategorizeInput(
                    transcribed_text=full_transcription.transcription,
                )
                category_output = categorize_call.categorize(category_input_data)
                results["category"] = {"category": category_output.category}
                yield _format_result("category", results["category"])
                await asyncio.sleep(1)
            except categorize_call.CategorizationError as e:
                yield _format_error("Call categorization failed", str(e))

        # Generate Summary Table
        summary_table = _generate_summary_table(
            speaker_speech_data, speed_results, pii_results, profanity_results,
            phrases_results, sentiment_results,
        )
        yield _format_result("summary", summary_table)

        # Cleanup
        Path(file_path).unlink()
        yield _format_result("complete", "Call processing completed.")

    except Exception as e:
        yield _format_error("Unexpected error", str(e))
        raise  # Re-raise the exception to avoid hiding it


def _format_result(step: str, result: str) -> str:
    """Format a result as a JSON-encoded string.

    Args:
        step: The step name.
        result: The result of the step.

    Returns:
        str: JSON-encoded result.

    """
    return f"data: {json.dumps({'step': step, 'result': result})}\n\n"


def _format_error(message: str, error: str) -> str:
    """Format an error as a JSON-encoded string.

    Args:
        message: The error message.
        error: The error details.

    Returns:
        str: JSON-encoded error.

    """
    return f"data: {json.dumps({'step': 'error', 'result': f'{message}: {error}'})}\n\n"


def _generate_summary_table(
    speaker_speech_data: dict | None,
    speed_results: dict | None,
    pii_results: dict | None,
    profanity_results: dict | None,
    phrases_results: dict | None,
    sentiment_results: dict | None,
) -> dict[str, list[list[str]]]:
    """Generate a summary table of the analysis results.

    Args:
        speaker_speech_data: Speaker speech data.
        speed_results: Speaking speed results.
        pii_results: PII check results.
        profanity_results: Profanity check results.
        phrases_results: Required phrases results.
        sentiment_results: Sentiment analysis results.

    Returns:
        dict[str, list[list[str]]]: Summary table.

    """
    summary_table = {
        "columns": ["Analysis", "Speaker 1", "Speaker 2"],
        "rows": [],
    }

    # Extract speaker-specific data
    speaker_1_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_00", None)
    speaker_2_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_01", None)

    # Add rows to the summary table
    summary_table["rows"].append([
        "Speech Data",
        f"Length: {speaker_1_data.length if speaker_1_data else 'N/A'}\n"
        f"Time: {speaker_1_data.time_period if speaker_1_data else 'N/A'}",
        f"Length: {speaker_2_data.length if speaker_2_data else 'N/A'}\n"
        f"Time: {speaker_2_data.time_period if speaker_2_data else 'N/A'}",
    ])

    summary_table["rows"].append([
        "Speaking Speed (WPM)",
        f"{speed_results.speaking_speeds.get('SPEAKER_00', 'N/A')}",
        f"{speed_results.speaking_speeds.get('SPEAKER_01', 'N/A')}",
    ])

    summary_table["rows"].append([
        "PII Check",
        f"Detected: {pii_results.detected if pii_results else 'N/A'}",
        f"Detected: {pii_results.detected if pii_results else 'N/A'}",
    ])

    summary_table["rows"].append([
        "Profanity Check",
        f"Detected: {profanity_results.detected if profanity_results else 'N/A'}",
        f"Detected: {profanity_results.detected if profanity_results else 'N/A'}",
    ])

    summary_table["rows"].append([
        "Required Phrases",
        f"Present: {phrases_results.required_phrases_present}\n"
        f"Phrases: {phrases_results.present_phrases if phrases_results else 'N/A'}",
        f"Present: {phrases_results.required_phrases_present}\n"
        f"Phrases: {phrases_results.present_phrases if phrases_results else 'N/A'}",
    ])

    summary_table["rows"].append([
        "Sentiment Analysis",
        f"Polarity: {sentiment_results.polarity if sentiment_results else 'N/A'}\n"
        f"Subjectivity: {sentiment_results.subjectivity\
                    if sentiment_results else 'N/A'}\n"
        f"Overall: {sentiment_results.overall_sentiment\
                    if sentiment_results else 'N/A'}",
        f"Polarity: {sentiment_results.polarity\
                    if sentiment_results else 'N/A'}\n"
        f"Subjectivity: {sentiment_results.subjectivity\
                    if sentiment_results else 'N/A'}\n"
        f"Overall:{sentiment_results.overall_sentiment\
                if sentiment_results else 'N/A'}",
    ])

    return summary_table


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
