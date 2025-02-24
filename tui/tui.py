"""Text-based User Interface (TUI) for speech analysis."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import warnings

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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

# Suppress all warnings
warnings.filterwarnings("ignore")

console = Console()


def display_transcription(audio_file_path: str) -> None:
    """Display the transcription of the audio file."""
    console.print(Panel.fit("[bold cyan]--- Running Transcription ---[/bold cyan]"))
    transcription_input = transcription.TranscribeAudioSegmentInput(
        audio_file=audio_file_path,
    )
    full_transcription = transcription.transcribe_audio_segment(transcription_input)
    console.print(f"[bold]Transcription:[/bold]\n{full_transcription.transcription}")
    return full_transcription


def display_diarization(audio_file_path: str) -> tuple:
    """Display the diarization results of the audio file."""
    console.print(
        Panel.fit("[bold cyan]--- Running Speaker Diarization ---[/bold cyan]"),
    )
    diarization_input = speaker_diarization.DiarizeInput(audio_file=audio_file_path)
    diarization_results = speaker_diarization.diarize(diarization_input)
    console.print("[bold]Diarization Results:[/bold]\n")

    # Display speaker segments in a table
    segments_table = Table(
        title="Speaker Segments",
        show_header=True,
        header_style="bold magenta",
    )
    segments_table.add_column("Start Time (s)", style="cyan")
    segments_table.add_column("End Time (s)", style="cyan")
    segments_table.add_column("Speaker", style="green")
    for segment in diarization_results.speaker_segments:
        segments_table.add_row(
            f"{segment.start_time:.2f}",
            f"{segment.end_time:.2f}",
            segment.speaker,
        )
    console.print(segments_table)

    # Display metrics in a table
    metrics_table = Table(
        title="Call Metrics",
        show_header=True,
        header_style="bold magenta",
    )
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_row(
        "Customer-to-Agent Speaking Ratio",
        str(diarization_results.speaking_ratio),
    )
    metrics_table.add_row(
        "Agent Interruptions",
        str(diarization_results.interruptions),
    )
    metrics_table.add_row(
        "Time to First Token (TTFT)",
        f"{diarization_results.time_to_first_token:.2f}s",
    )
    console.print(metrics_table)
    return diarization_results


def display_speaker_speed(
    audio_file_path: str, diarization_results: tuple,
) -> tuple:
    """Display the speaking speed analysis of the audio file."""
    console.print(
        Panel.fit("[bold cyan]--- Running Speaker Speed Analysis ---[/bold cyan]"),
    )
    speech_data_input = GetSpeakerSpeechDataInput(
        audio_file=audio_file_path,
        speaker_segments=diarization_results.speaker_segments,
    )
    speaker_speech_data = get_speaker_speech_data(speech_data_input)
    speed_results = speaker_speed.calculate_speaking_speed(speaker_speech_data)
    speed_table = Table(title="Speaker Speeds")
    speed_table.add_column("Speaker", style="cyan")
    speed_table.add_column("Speed (words per minute)", style="magenta")
    for speaker, speed in speed_results.speaking_speeds.items():
        speed_table.add_row(speaker, f"{speed:.2f}")
    console.print(speed_table)
    return speaker_speech_data, speed_results


def display_pii_check(transcription_text: str) -> None:
    """Display the PII check results."""
    console.print(Panel.fit("[bold cyan]--- Running PII Check ---[/bold cyan]"))
    pii_data_input = pii_check.CheckPIIInput(transcribed_text=transcription_text)
    pii_results = pii_check.check_pii(pii_data_input)
    console.print(
        f"[bold]PII Detected:[/bold] {pii_results.detected}\n"
        f"[bold]Masked Text:[/bold]\n{pii_results.masked_text}",
    )


def display_profanity_check(transcription_text: str) -> None:
    """Display the profanity check results."""
    console.print(Panel.fit("[bold cyan]--- Running Profanity Check ---[/bold cyan]"))
    profanity_input_data = profanity_check.CheckProfanityInput(
        transcribed_text=transcription_text,
    )
    profanity_results = profanity_check.check_profanity(profanity_input_data)
    console.print(
        f"[bold]Profanity Detected:[/bold] {profanity_results.detected}\n"
        f"[bold]Censored Text:[/bold]\n{profanity_results.censored_text}",
    )


def display_required_phrases_check(transcription_text: str) -> None:
    """Display the required phrases check results."""
    console.print(
        Panel.fit("[bold cyan]--- Running Required Phrases Check ---[/bold cyan]"),
    )
    phrases_input_data = CheckRequiredPhrasesInput(transcribed_text=transcription_text)
    phrases_results = check_required_phrases(phrases_input_data)
    console.print(
        f"[bold]Required Phrases Present:[/bold] "
        f"{phrases_results.required_phrases_present}\n"
        f"[bold]Phrases:[/bold] "
        f"{phrases_results.present_phrases
        if phrases_results.required_phrases_present else 'N/A'}",
    )


def display_sentiment_analysis(transcription_text: str) -> None:
    """Display the sentiment analysis results."""
    console.print(Panel.fit(
    "[bold cyan]--- Running Sentiment Analysis ---[/bold cyan]"))
    sentiment_input_data = sentiment_analysis.AnalyseSentimentInput(
        transcribed_text=transcription_text,
    )
    sentiment_results = sentiment_analysis.analyse_sentiment(sentiment_input_data)
    console.print(
        f"[bold]Polarity:[/bold] {sentiment_results.polarity}\n"
        f"[bold]Subjectivity:[/bold] {sentiment_results.subjectivity}\n"
        f"[bold]Overall Sentiment:[/bold] {sentiment_results.overall_sentiment}",
    )


def display_call_categorization(transcription_text: str) -> None:
    """Display the call categorization results."""
    console.print(
        Panel.fit("[bold cyan]--- Running Call Categorization ---[/bold cyan]"),
    )
    category_input_data = categorize_call.CategorizeInput(
        transcribed_text=transcription_text,
    )
    category = categorize_call.categorize(category_input_data)
    console.print(f"[bold]Call Category:[/bold] {category}")


def display_summary_table(
    speaker_speech_data: dict, speed_results: dict,
) -> None:
    """Display the summary table for quick overview."""
    console.print(Panel.fit("[bold cyan]--- Summary Table ---[/bold cyan]"))
    summary_table = Table(
        title="Summary of Analysis",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )
    summary_table.add_column("Analysis", style="cyan")
    summary_table.add_column("Speaker 1", style="green")
    summary_table.add_column("Speaker 2", style="green")

    # Extract speaker-specific data
    speaker_1_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_00", None)
    speaker_2_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_01", None)

    # Add Speech Data row
    summary_table.add_row(
        "Speech Data",
        f"Length: {speaker_1_data.length if speaker_1_data else 'N/A'}\n"
        f"Time: {speaker_1_data.time_period if speaker_1_data else 'N/A'}",
        f"Length: {speaker_2_data.length if speaker_2_data else 'N/A'}\n"
        f"Time: {speaker_2_data.time_period if speaker_2_data else 'N/A'}",
    )

    # Add Speaking Speed row
    summary_table.add_row(
        "Speaking Speed (WPM)",
        f"{speed_results.speaking_speeds.get('SPEAKER_00', 'N/A')}",
        f"{speed_results.speaking_speeds.get('SPEAKER_01', 'N/A')}",
    )

    # Add PII Check row
    pii_speaker_1 = (
        pii_check.check_pii(
            pii_check.CheckPIIInput(
                transcribed_text=speaker_1_data.speech if speaker_1_data else "",
            ),
        )
        if speaker_1_data
        else None
    )
    pii_speaker_2 = (
        pii_check.check_pii(
            pii_check.CheckPIIInput(
                transcribed_text=speaker_2_data.speech if speaker_2_data else "",
            ),
        )
        if speaker_2_data
        else None
    )
    summary_table.add_row(
        "PII Check",
        f"Detected: {pii_speaker_1.detected if pii_speaker_1 else 'N/A'}",
        f"Detected: {pii_speaker_2.detected if pii_speaker_2 else 'N/A'}",
    )

    # Add Profanity Check row
    profanity_speaker_1 = (
        profanity_check.check_profanity(
            profanity_check.CheckProfanityInput(
                transcribed_text=speaker_1_data.speech if speaker_1_data else "",
            ),
        )
        if speaker_1_data
        else None
    )
    profanity_speaker_2 = (
        profanity_check.check_profanity(
            profanity_check.CheckProfanityInput(
                transcribed_text=speaker_2_data.speech if speaker_2_data else "",
            ),
        )
        if speaker_2_data
        else None
    )
    summary_table.add_row(
        "Profanity Check",
        f"Detected: {profanity_speaker_1.detected if profanity_speaker_1 else 'N/A'}",
        f"Detected: {profanity_speaker_2.detected if profanity_speaker_2 else 'N/A'}",
    )

    # Add Required Phrases Check row
    phrases_speaker_1 = (
        check_required_phrases(
            CheckRequiredPhrasesInput(
                transcribed_text=speaker_1_data.speech if speaker_1_data else "",
            ),
        )
        if speaker_1_data
        else None
    )
    phrases_speaker_2 = (
        check_required_phrases(
            CheckRequiredPhrasesInput(
                transcribed_text=speaker_2_data.speech if speaker_2_data else "",
            ),
        )
        if speaker_2_data
        else None
    )
    required_phrases_speaker_1 = (
        f"Present: {phrases_speaker_1.required_phrases_present}\n"
        f"Phrases: {phrases_speaker_1.present_phrases
        if phrases_speaker_1 and phrases_speaker_1.required_phrases_present else 'N/A'}"
        if phrases_speaker_1
        else "N/A"
    )
    required_phrases_speaker_2 = (
        f"Present: {phrases_speaker_2.required_phrases_present}\n"
        f"Phrases: {phrases_speaker_2.present_phrases
        if phrases_speaker_2 and phrases_speaker_2.required_phrases_present else 'N/A'}"
        if phrases_speaker_2
        else "N/A"
    )
    summary_table.add_row(
        "Required Phrases",
        required_phrases_speaker_1,
        required_phrases_speaker_2,
    )

    # Add Sentiment Analysis row
    sentiment_speaker_1 = (
        sentiment_analysis.analyse_sentiment(
            sentiment_analysis.AnalyseSentimentInput(
                transcribed_text=speaker_1_data.speech if speaker_1_data else "",
            ),
        )
        if speaker_1_data
        else None
    )
    sentiment_speaker_2 = (
        sentiment_analysis.analyse_sentiment(
            sentiment_analysis.AnalyseSentimentInput(
                transcribed_text=speaker_2_data.speech if speaker_2_data else "",
            ),
        )
        if speaker_2_data
        else None
    )
    summary_table.add_row(
        "Sentiment Analysis",
        f"Polarity: {sentiment_speaker_1.polarity if sentiment_speaker_1 else 'N/A'}\n"
        f"Subjectivity: {sentiment_speaker_1.subjectivity
        if sentiment_speaker_1 else 'N/A'}\n"
        f"Overall: {sentiment_speaker_1.overall_sentiment
        if sentiment_speaker_1 else 'N/A'}",
        f"Polarity: {sentiment_speaker_2.polarity
        if sentiment_speaker_2 else 'N/A'}\n"
        f"Subjectivity: {sentiment_speaker_2.subjectivity
        if sentiment_speaker_2 else 'N/A'}\n"
        f"Overall: {sentiment_speaker_2.overall_sentiment
        if sentiment_speaker_2 else 'N/A'}",
    )

    # Display the summary table
    console.print(summary_table)


def run_all(audio_file_path: str) -> None:
    """Run all analysis functions on a given audio file."""
    full_transcription = display_transcription(audio_file_path)
    diarization_results = display_diarization(audio_file_path)
    speaker_speech_data, speed_results = display_speaker_speed(
        audio_file_path, diarization_results,
    )
    display_pii_check(full_transcription.transcription)
    display_profanity_check(full_transcription.transcription)
    display_required_phrases_check(full_transcription.transcription)
    display_sentiment_analysis(full_transcription.transcription)
    display_call_categorization(full_transcription.transcription)
    display_summary_table(speaker_speech_data, speed_results)


def tui_interface() -> None:
    """Interactive Text-based UI."""
    choices = [
        "Run All Analyses",
        "Transcribe Audio",
        "Perform Speaker Diarization",
        "Analyze Speaker Speed",
        "Check PII",
        "Check Profanity",
        "Check Required Phrases",
        "Analyze Sentiment",
        "Categorize Call",
        "Exit",
    ]

    while True:
        choice = questionary.select("Choose an analysis to run:", choices).ask()

        if choice == "Run All Analyses":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            run_all(audio_file)

        elif choice == "Transcribe Audio":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            display_transcription(audio_file)

        elif choice == "Perform Speaker Diarization":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            display_diarization(audio_file)

        elif choice == "Analyze Speaker Speed":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            diarization_results = display_diarization(audio_file)
            display_speaker_speed(audio_file, diarization_results)

        elif choice == "Check PII":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            transcription_input = transcription.TranscribeAudioSegmentInput(
                audio_file=audio_file,
            )
            transcription_result = transcription.transcribe_audio_segment(
                transcription_input,
            )
            display_pii_check(transcription_result.transcription)

        elif choice == "Check Profanity":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            transcription_input = transcription.TranscribeAudioSegmentInput(
                audio_file=audio_file,
            )
            transcription_result = transcription.transcribe_audio_segment(
                transcription_input,
            )
            display_profanity_check(transcription_result.transcription)

        elif choice == "Check Required Phrases":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            transcription_input = transcription.TranscribeAudioSegmentInput(
                audio_file=audio_file,
            )
            transcription_result = transcription.transcribe_audio_segment(
                transcription_input,
            )
            display_required_phrases_check(transcription_result.transcription)

        elif choice == "Analyze Sentiment":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            transcription_input = transcription.TranscribeAudioSegmentInput(
                audio_file=audio_file,
            )
            transcription_result = transcription.transcribe_audio_segment(
                transcription_input,
            )
            display_sentiment_analysis(transcription_result.transcription)

        elif choice == "Categorize Call":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            transcription_input = transcription.TranscribeAudioSegmentInput(
                audio_file=audio_file,
            )
            transcription_result = transcription.transcribe_audio_segment(
                transcription_input,
            )
            display_call_categorization(transcription_result.transcription)

        elif choice == "Exit":
            break


if __name__ == "__main__":
    tui_interface()
