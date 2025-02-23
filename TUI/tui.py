import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from call_processor_modules import categorize_call
from call_processor_modules import pii_check
from call_processor_modules import profanity_check
from call_processor_modules.required_phrases import check_required_phrases,CheckRequiredPhrasesInput
from call_processor_modules import sentiment_analysis
from call_processor_modules import speaker_diarization
from call_processor_modules import speaker_speed
from call_processor_modules import transcription
from call_processor_modules.speaker import get_speaker_speech_data,GetSpeakerSpeechDataInput
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import warnings
import logging
import os

# Suppress all warnings
warnings.filterwarnings("ignore")

console = Console()

def run_all(audio_file_path):
    """Run all analysis functions on a given audio file."""
    
    console.print(Panel.fit("[bold cyan]--- Running Transcription ---[/bold cyan]"))
    transcription_input = transcription.TranscribeAudioSegmentInput(audio_file=audio_file_path)
    full_transcription = transcription.transcribe_audio_segment(transcription_input)
    console.print(f"[bold]Transcription:[/bold]\n{full_transcription.transcription}")

    console.print(Panel.fit("[bold cyan]--- Running Speaker Diarization ---[/bold cyan]"))
    diarization_input = speaker_diarization.DiarizeInput(audio_file=audio_file_path)
    diarization_results = speaker_diarization.diarize(diarization_input)
    console.print(f"[bold]Diarization Results:[/bold]\n")

    # Display speaker segments in a table
    segments_table = Table(title="Speaker Segments", show_header=True, header_style="bold magenta")
    segments_table.add_column("Start Time (s)", style="cyan")
    segments_table.add_column("End Time (s)", style="cyan")
    segments_table.add_column("Speaker", style="green")
    for segment in diarization_results.speaker_segments:
        segments_table.add_row(f"{segment.start_time:.2f}", f"{segment.end_time:.2f}", segment.speaker)
    console.print(segments_table)

    # Display metrics in a table
    metrics_table = Table(title="Call Metrics", show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_row("Customer-to-Agent Speaking Ratio", str(diarization_results.speaking_ratio))
    metrics_table.add_row("Agent Interruptions", str(diarization_results.interruptions))
    metrics_table.add_row("Time to First Token (TTFT)", f"{diarization_results.time_to_first_token:.2f}s")
    console.print(metrics_table)

    # Generate SpeakerSpeechData
    console.print(Panel.fit("[bold cyan]--- Generating Speaker Speech Data ---[/bold cyan]"))
    speech_data_input = GetSpeakerSpeechDataInput(
        audio_file=audio_file_path,
        speaker_segments=diarization_results.speaker_segments
    )
    speaker_speech_data = get_speaker_speech_data(speech_data_input)
    console.print(f"[bold]Speaker Speech Data:[/bold]\n{speaker_speech_data}")

    # Calculate Speaking Speed
    console.print(Panel.fit("[bold cyan]--- Running Speaker Speed Analysis ---[/bold cyan]"))
    speed_results = speaker_speed.calculate_speaking_speed(speaker_speech_data)
    speed_table = Table(title="Speaker Speeds")
    speed_table.add_column("Speaker", style="cyan")
    speed_table.add_column("Speed (words per minute)", style="magenta")
    for speaker, speed in speed_results.speaking_speeds.items():
        speed_table.add_row(speaker, f"{speed:.2f}")
    console.print(speed_table)

    # Perform PII Check
    console.print(Panel.fit("[bold cyan]--- Running PII Check ---[/bold cyan]"))
    pii_data_input = pii_check.CheckPIIInput(transcribed_text=full_transcription.transcription)
    pii_results = pii_check.check_pii(pii_data_input)
    console.print(f"[bold]PII Detected:[/bold] {pii_results.detected}\n[bold]Masked Text:[/bold]\n{pii_results.masked_text}")

    # Perform Profanity Check
    console.print(Panel.fit("[bold cyan]--- Running Profanity Check ---[/bold cyan]"))
    profanity_input_data = profanity_check.CheckProfanityInput(transcribed_text=full_transcription.transcription)
    profanity_results = profanity_check.check_profanity(profanity_input_data)
    console.print(f"[bold]Profanity Detected:[/bold] {profanity_results.detected}\n[bold]Censored Text:[/bold]\n{profanity_results.censored_text}")

    # Perform Required Phrases Check
    console.print(Panel.fit("[bold cyan]--- Running Required Phrases Check ---[/bold cyan]"))
    phrases_input_data = CheckRequiredPhrasesInput(transcribed_text=full_transcription.transcription)
    phrases_results = check_required_phrases(phrases_input_data)
    console.print(f"[bold]Required Phrases Present:[/bold] {phrases_results.required_phrases_present}\n[bold]Phrases:[/bold] {phrases_results.present_phrases if phrases_results.required_phrases_present else 'N/A'}")

    # Perform Sentiment Analysis
    console.print(Panel.fit("[bold cyan]--- Running Sentiment Analysis ---[/bold cyan]"))
    sentiment_input_data = sentiment_analysis.AnalyseSentimentInput(transcribed_text=full_transcription.transcription)
    sentiment_results = sentiment_analysis.analyse_sentiment(sentiment_input_data)
    console.print(f"[bold]Polarity:[/bold] {sentiment_results.polarity}\n[bold]Subjectivity:[/bold] {sentiment_results.subjectivity}\n[bold]Overall Sentiment:[/bold] {sentiment_results.overall_sentiment}")

    # Perform Call Categorization
    console.print(Panel.fit("[bold cyan]--- Running Call Categorization ---[/bold cyan]"))
    category_input_data = categorize_call.CategorizeInput(transcribed_text=full_transcription.transcription)
    category = categorize_call.categorize(category_input_data)
    console.print(f"[bold]Call Category:[/bold] {category}")

    # Create a summary table for quick overview
    console.print(Panel.fit("[bold cyan]--- Summary Table ---[/bold cyan]"))
    summary_table = Table(title="Summary of Analysis", show_header=True, header_style="bold magenta", show_lines=True)
    summary_table.add_column("Analysis", style="cyan")
    summary_table.add_column("Speaker 1", style="green")
    summary_table.add_column("Speaker 2", style="green")

    # Extract speaker-specific data
    speaker_1_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_00", None)
    speaker_2_data = speaker_speech_data.speaker_speech_data.get("SPEAKER_01", None)

    # Add Speech Data row
    summary_table.add_row(
        "Speech Data",
        f"Length: {speaker_1_data.length if speaker_1_data else 'N/A'}\nTime: {speaker_1_data.time_period if speaker_1_data else 'N/A'}",
        f"Length: {speaker_2_data.length if speaker_2_data else 'N/A'}\nTime: {speaker_2_data.time_period if speaker_2_data else 'N/A'}"
    )

    # Add Speaking Speed row
    summary_table.add_row(
        "Speaking Speed (WPM)",
        f"{speed_results.speaking_speeds.get('SPEAKER_00', 'N/A')}",
        f"{speed_results.speaking_speeds.get('SPEAKER_01', 'N/A')}"
    )

    # Add PII Check row
    pii_speaker_1 = pii_check.check_pii(pii_check.CheckPIIInput(transcribed_text=speaker_1_data.speech if speaker_1_data else "")) if speaker_1_data else None
    pii_speaker_2 = pii_check.check_pii(pii_check.CheckPIIInput(transcribed_text=speaker_2_data.speech if speaker_2_data else "")) if speaker_2_data else None
    summary_table.add_row(
        "PII Check",
        f"Detected: {pii_speaker_1.detected if pii_speaker_1 else 'N/A'}",
        f"Detected: {pii_speaker_2.detected if pii_speaker_2 else 'N/A'}"
    )

    # Add Profanity Check row
    profanity_speaker_1 = profanity_check.check_profanity(profanity_check.CheckProfanityInput(transcribed_text=speaker_1_data.speech if speaker_1_data else "")) if speaker_1_data else None
    profanity_speaker_2 = profanity_check.check_profanity(profanity_check.CheckProfanityInput(transcribed_text=speaker_2_data.speech if speaker_2_data else "")) if speaker_2_data else None
    summary_table.add_row(
        "Profanity Check",
        f"Detected: {profanity_speaker_1.detected if profanity_speaker_1 else 'N/A'}",
        f"Detected: {profanity_speaker_2.detected if profanity_speaker_2 else 'N/A'}"
    )

    # Add Required Phrases Check row
    phrases_speaker_1 = check_required_phrases(CheckRequiredPhrasesInput(transcribed_text=speaker_1_data.speech if speaker_1_data else "")) if speaker_1_data else None
    phrases_speaker_2 = check_required_phrases(CheckRequiredPhrasesInput(transcribed_text=speaker_2_data.speech if speaker_2_data else "")) if speaker_2_data else None
    required_phrases_speaker_1 = f"Present: {phrases_speaker_1.required_phrases_present}\nPhrases: {phrases_speaker_1.present_phrases if phrases_speaker_1 and phrases_speaker_1.required_phrases_present else 'N/A'}" if phrases_speaker_1 else "N/A"
    required_phrases_speaker_2 = f"Present: {phrases_speaker_2.required_phrases_present}\nPhrases: {phrases_speaker_2.present_phrases if phrases_speaker_2 and phrases_speaker_2.required_phrases_present else 'N/A'}" if phrases_speaker_2 else "N/A"
    summary_table.add_row(
        "Required Phrases",
        required_phrases_speaker_1,
        required_phrases_speaker_2
    )

    # Add Sentiment Analysis row
    sentiment_speaker_1 = sentiment_analysis.analyse_sentiment(sentiment_analysis.AnalyseSentimentInput(transcribed_text=speaker_1_data.speech if speaker_1_data else "")) if speaker_1_data else None
    sentiment_speaker_2 = sentiment_analysis.analyse_sentiment(sentiment_analysis.AnalyseSentimentInput(transcribed_text=speaker_2_data.speech if speaker_2_data else "")) if speaker_2_data else None
    summary_table.add_row(
        "Sentiment Analysis",
        f"Polarity: {sentiment_speaker_1.polarity if sentiment_speaker_1 else 'N/A'}\nSubjectivity: {sentiment_speaker_1.subjectivity if sentiment_speaker_1 else 'N/A'}\nOverall: {sentiment_speaker_1.overall_sentiment if sentiment_speaker_1 else 'N/A'}",
        f"Polarity: {sentiment_speaker_2.polarity if sentiment_speaker_2 else 'N/A'}\nSubjectivity: {sentiment_speaker_2.subjectivity if sentiment_speaker_2 else 'N/A'}\nOverall: {sentiment_speaker_2.overall_sentiment if sentiment_speaker_2 else 'N/A'}"
    )

    # Display the summary table
    console.print(summary_table)



def tui_interface():
    """Interactive Text-based UI"""
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
        "Exit"
    ]
    
    while True:
        choice = questionary.select("Choose an analysis to run:", choices).ask()

        if choice == "Run All Analyses":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            run_all(audio_file)

        elif choice == "Transcribe Audio":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            console.print(Panel.fit("[bold cyan]--- Transcription ---[/bold cyan]"))
            transcription_input = transcription.TranscribeAudioSegmentInput(audio_file=audio_file)
            transcription_result = transcription.transcribe_audio_segment(transcription_input)
            console.print(f"[bold]Transcription:[/bold]\n{transcription_result.transcription}")

        elif choice == "Perform Speaker Diarization":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            console.print(Panel.fit("[bold cyan]--- Speaker Diarization ---[/bold cyan]"))
            
            # Call the diarize function
            diarization_input = speaker_diarization.DiarizeInput(audio_file=audio_file)
            diarization_results = speaker_diarization.diarize(diarization_input)
            
            # Display diarization results
            console.print(Panel.fit("[bold green]Diarization Results[/bold green]"))
            console.print(diarization_results)
            
            # Display segments in a table
            segments_table = Table(title="Speaker Segments", show_header=True, header_style="bold magenta")
            segments_table.add_column("Start Time (s)", style="cyan")
            segments_table.add_column("End Time (s)", style="cyan")
            segments_table.add_column("Speaker", style="green")
            for segment in diarization_results.speaker_segments:
                segments_table.add_row(f"{segment.start_time:.2f}", f"{segment.end_time:.2f}", segment.speaker)
            console.print(segments_table)
            
            # Display metrics in a table
            metrics_table = Table(title="Call Metrics", show_header=True, header_style="bold magenta")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")
            metrics_table.add_row("Customer-to-Agent Speaking Ratio", str(diarization_results.speaking_ratio))
            metrics_table.add_row("Agent Interruptions", str(diarization_results.interruptions))
            metrics_table.add_row("Time to First Token (TTFT)", f"{diarization_results.time_to_first_token:.2f}s")
            console.print(metrics_table)

        elif choice == "Analyze Speaker Speed":
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            console.print(Panel.fit("[bold cyan]--- Speaker Speed Analysis ---[/bold cyan]"))
            
            # Perform diarization first
            diarization_input = speaker_diarization.DiarizeInput(audio_file=audio_file)
            diarization_results = speaker_diarization.diarize(diarization_input)
            
            # Generate SpeakerSpeechData
            speech_data_input = GetSpeakerSpeechDataInput(
                audio_file=audio_file,
                speaker_segments=diarization_results.speaker_segments
            )
            speaker_speech_data = get_speaker_speech_data(speech_data_input)
            
            # Calculate Speaking Speed
            speed_results = speaker_speed.calculate_speaking_speed(speaker_speech_data)
            speed_table = Table(title="Speaker Speeds")
            speed_table.add_column("Speaker", style="cyan")
            speed_table.add_column("Speed (words per minute)", style="magenta")
            for speaker, speed in speed_results.speaking_speeds.items():
                speed_table.add_row(speaker, f"{speed:.2f}")
            console.print(speed_table)

        elif choice in ["Check PII", "Check Profanity", "Check Required Phrases", "Analyze Sentiment", "Categorize Call"]:
            # Always ask for an audio file
            audio_file = questionary.text("Enter the path to the audio file:").ask()
            
            # Run transcription
            # console.print(Panel.fit("[bold cyan]--- Transcription ---[/bold cyan]"))
            transcription_input = transcription.TranscribeAudioSegmentInput(audio_file=audio_file)
            transcription_result = transcription.transcribe_audio_segment(transcription_input)
            text = transcription_result.transcription
            # console.print(f"[bold]Transcription:[/bold]\n{text}")

            if choice == "Check PII":
                console.print(Panel.fit("[bold cyan]--- PII Check ---[/bold cyan]"))
                pii_data_input = pii_check.CheckPIIInput(transcribed_text=text)
                pii_detected, masked_text = pii_check.check_pii(pii_data_input)
                console.print(f"[bold]PII Detected:[/bold] {pii_detected}\n[bold]Masked Text:[/bold]\n{masked_text}")

            elif choice == "Check Profanity":
                console.print(Panel.fit("[bold cyan]--- Profanity Check ---[/bold cyan]"))
                profanity_input_data = profanity_check.CheckProfanityInput(transcribed_text=text)
                profanity_detected, censored_text = profanity_check.check_profanity(profanity_input_data)
                console.print(f"[bold]Profanity Detected:[/bold] {profanity_detected}\n[bold]Censored Text:[/bold]\n{censored_text}")

            elif choice == "Check Required Phrases":
                console.print(Panel.fit("[bold cyan]--- Required Phrases Check ---[/bold cyan]"))
                phrases_input_data = CheckRequiredPhrasesInput(transcribed_text=text)
                phrases_present = check_required_phrases(phrases_input_data)
                console.print(f"[bold]Required Phrases Present:[/bold] {phrases_present}")

            elif choice == "Analyze Sentiment":
                console.print(Panel.fit("[bold cyan]--- Sentiment Analysis ---[/bold cyan]"))
                sentiment_input_data = sentiment_analysis.AnalyseSentimentInput(transcribed_text=text)
                polarity, subjectivity, overall_sentiment = sentiment_analysis.analyse_sentiment(sentiment_input_data)
                console.print(f"[bold]Polarity:[/bold] {polarity}\n[bold]Subjectivity:[/bold] {subjectivity}\n[bold]Overall Sentiment:[/bold] {overall_sentiment}")

            elif choice == "Categorize Call":
                console.print(Panel.fit("[bold cyan]--- Call Categorization ---[/bold cyan]"))
                category_input_data = categorize_call.CategorizeInput(transcribed_text=text)
                category = categorize_call.categorize(category_input_data)
                console.print(f"[bold]Call Category:[/bold] {category}")

        elif choice == "Exit":
            break

if __name__ == "__main__":
    tui_interface()