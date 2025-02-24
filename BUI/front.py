import json
from pathlib import Path

import requests
import streamlit as st

# from logger_config import get_logger

# logger = get_logger()

# Define the FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# List of available tasks
TASKS = [
    "Transcription",
    "Speaker Diarization",
    "Speaking Speed",
    "PII Check",
    "Profanity Check",
    "Required Phrases",
    "Sentiment Analysis",
    "Call Category",
]

# Initialize session state variables
if "transcription_output" not in st.session_state:
    st.session_state.update({
        "transcription_output": "Not selected",
        "transcription_status": "❌ Not selected",
        "diarization_output": "Not selected",
        "diarization_status": "❌ Not selected",
        "speaking_speed_output": "Not selected",
        "speaking_speed_status": "❌ Not selected",
        "pii_output": "Not selected",
        "pii_status": "❌ Not selected",
        "profanity_output": "Not selected",
        "profanity_status": "❌ Not selected",
        "phrases_output": "Not selected",
        "phrases_status": "❌ Not selected",
        "sentiment_output": "Not selected",
        "sentiment_status": "❌ Not selected",
        "category_output": "Not selected",
        "category_status": "❌ Not selected",
        "summary_output": "Summary table will appear here...",
        "summary_status": "❌ Not selected",
        "process_output": "Not selected",
        "process_status": "❌ Not selected",
    })

def initialize_results(selected_tasks):
    """Initialize the results dictionary and set UI status for selected tasks."""
    results = {
        "transcription": "Not selected",
        "diarization": "Not selected",
        "speaking_speed": "Not selected",
        "pii": "Not selected",
        "profanity": "Not selected",
        "required_phrases": "Not selected",
        "sentiment": "Not selected",
        "category": "Not selected",
        "summary": "Not selected",
        "message": "Not selected",
    }

    status_mapping = {
        "Transcription": "transcription_status",
        "Speaker Diarization": "diarization_status",
        "Speaking Speed": "speaking_speed_status",
        "PII Check": "pii_status",
        "Profanity Check": "profanity_status",
        "Required Phrases": "phrases_status",
        "Sentiment Analysis": "sentiment_status",
        "Call Category": "category_status",
    }

    for task in selected_tasks:
        key = status_mapping.get(task)
        if key:
            results[key] = "Processing..."
            setattr(st.session_state, key, "⏳ Processing")

    return results

def prepare_audio_file(audio_file):
    """Prepare the audio file for uploading."""
    if isinstance(audio_file, str):  # If it's a file path, open it
        audio_path = Path(audio_file)
        return {"file": open(audio_path, "rb")}  # Keep the file open
    return {"file": audio_file}


def send_audio_to_backend(files, selected_tasks):
    """Send the audio file and tasks to the backend for processing."""
    return requests.post(
        f"{BACKEND_URL}/process_call/",
        files=files,
        data={"tasks": json.dumps(selected_tasks)},
        timeout=30,  # Added timeout to fix S113
        stream=True,
    )

def update_transcription(result, results):
    """Update transcription-related outputs."""
    results["transcription"] = result
    st.session_state.transcription_output = (
        f"<span style='color:green;'>*Transcription:*</span>"
        f"{result}"
    )
    st.session_state.transcription_status = "✅ Completed"


def update_diarization(result, results):
    """Update diarization-related outputs."""
    results["diarization"] = result
    st.session_state.diarization_output = {
        "speaker_segments": result["speaker_segments"],
        "speaking_ratio": result["speaking_ratio"],
        "interruptions": result["interruptions"],
        "time_to_first_token": result["time_to_first_token"],
    }
    st.session_state.diarization_status = "✅ Completed"


def update_speaking_speed(result, results):
    """Update speaking speed-related outputs."""
    results["speaking_speed"] = result
    st.session_state.speaking_speed_output = (
        "<span style='color:blue;'>*Speaking Speed (WPM):*</span>"
    )
    st.session_state.speaking_speed_output += "\n".join(
        [
            f"- {speaker}:"
            f"<span style='color:orange;'>{speed:.2f} wpm</span>"
            for speaker, speed in result.items()
        ],
    )
    st.session_state.speaking_speed_status = "✅ Completed"


def update_pii(result, results):
    """Update PII-related outputs."""
    results["pii"] = result
    st.session_state.pii_output = (
        f"<span style='color:red;'>*PII Detected:*</span> "
        f"{result['detected']}"
        f"<span style='color:green;'>*Masked Text:*</span>\n"
        f"{result['masked_text']}"
    )
    st.session_state.pii_status = "✅ Completed"


def update_profanity(result, results):
    """Update profanity-related outputs."""
    results["profanity"] = result
    st.session_state.profanity_output = (
        f"<span style='color:red;'>*Profanity Detected:*</span>"
        f"{result['detected']}"
        f"<span style='color:green;'>*Censored Text:*</span>"
        f"{result['censored_text']}"
    )
    st.session_state.profanity_status = "✅ Completed"


def update_required_phrases(result, results):
    """Update required phrases-related outputs."""
    results["required_phrases"] = result
    st.session_state.phrases_output = (
        f"<span style='color:purple;'>*Required Phrases Present:*</span>"
        f"{result['required_phrases_present']}"
        f"<span style='color:green;'>*Phrases Found:*</span>"
    )
    st.session_state.phrases_output += "\n".join(
        [f"- {phrase}" for phrase in result["present_phrases"]],
    )
    st.session_state.phrases_status = "✅ Completed"


def update_sentiment(result, results):
    """Update sentiment-related outputs."""
    results["sentiment"] = result
    st.session_state.sentiment_output = (
        f"<span style='color:blue;'>Polarity:</span>"
        f"<span style='color:green;'>{result['polarity']:.2f}</span><br>"
        f"<span style='color:blue;'>Subjectivity:</span>"
        f"<span style='color:green;'>{result['subjectivity']:.2f}</span><br>"
        f"<span style='color:blue;'>Overall Sentiment:</span>"
        f"<span style='color:green;'>{result['overall_sentiment']}</span>"
    )
    st.session_state.sentiment_status = "✅ Completed"


def update_category(result, results):
    """Update category-related outputs."""
    results["category"] = result
    st.session_state.category_output = (
        f"<span style='color:purple;'>*Call Category:*</span>"
        f"{result['category']}"
    )
    st.session_state.category_status = "✅ Completed"


def update_summary(result, results):
    """Update summary-related outputs."""
    results["summary"] = result
    st.session_state.summary_output = result  # Store summary data
    st.session_state.summary_status = "✅ Completed"


def update_complete(result, results):
    """Update process completion-related outputs."""
    results["message"] = result
    st.session_state.process_output = (
        f"<span style='color:green;'>*Call Processing Status:*</span>"
        f"{result}"
    )
    st.session_state.process_status = "✅ Completed"


# Dictionary-based dispatch
STEP_HANDLERS = {
    "transcription": update_transcription,
    "diarization": update_diarization,
    "speaking_speed": update_speaking_speed,
    "pii": update_pii,
    "profanity": update_profanity,
    "required_phrases": update_required_phrases,
    "sentiment": update_sentiment,
    "category": update_category,
    "summary": update_summary,
    "complete": update_complete,
}


def take(result, results, step):
    """Update the results dictionary and output variables based on the step."""
    handler = STEP_HANDLERS.get(step)
    if handler:
        handler(result, results)
    else:
        error_message = f"Unknown step: {step}"
        raise ValueError(error_message)

# Function to process the audio file and update the UI progressively
def process_audio(audio_file, selected_tasks):
    """Process an audio file by sending it to the backend and updating the UI.

    Args:
        audio_file (str or Path): Path to the audio file to be processed.
        selected_tasks (list): List of tasks to be performed on the audio.

    Returns:
        None

    """
    # Send the audio file to the backend for processing
    files = prepare_audio_file(audio_file)
    response = send_audio_to_backend(files, selected_tasks)

    results = initialize_results(selected_tasks)

    # Process the streaming response
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data:"):
                try:
                    # Extract the JSON part after "data:"
                    json_data = decoded_line[5:].strip()
                    data = json.loads(json_data)
                    step = data["step"]
                    result = data["result"]
                    take(result,results,step)
                except json.JSONDecodeError as e:
                    return e
    return None



# Streamlit App
st.set_page_config(page_title="Call Processing Dashboard", page_icon="🎙️", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("🎙️ Call Processing Dashboard")
    st.markdown("Upload an audio file and select the tasks you want to run.")

    # Audio input
    audio_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])

    # Task selection with checkboxes
    selected_tasks = [task for task in TASKS if st.checkbox(task,value=True)]

    # Submit button
    if st.button("Process Audio"):
        if audio_file is not None:
            with st.spinner("Processing..."):
                process_audio(audio_file.name, selected_tasks)
        else:
            st.warning("Please upload an audio file before processing.")

# Main content area
st.header("📝 Call Processing Results")

# Display outputs in a logical order

# 1. Transcription
st.subheader("📝 Transcription")
with st.expander("View Transcription", expanded=True):
    st.markdown(st.session_state.get("transcription_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("transcription_status", "").startswith("✅"):
        st.success(st.session_state["transcription_status"])
    else:
        st.warning(st.session_state["transcription_status"])

# 2. Speaker Diarization
st.subheader("🗣️ Speaker Diarization")
with st.expander("View Speaker Diarization", expanded=True):
    diarization_output = st.session_state.get("diarization_output", {})
    if isinstance(diarization_output, dict):
        # Display speaker segments in a table
        if "speaker_segments" in diarization_output:
            st.table(diarization_output["speaker_segments"])

        # Display additional metrics
        if "speaking_ratio" in diarization_output:
            st.markdown(
                f"<span style='color:blue;'>**Speaking Ratio:**</span>"
                f"{diarization_output['speaking_ratio']}</span>",\
                unsafe_allow_html=True)
        if "interruptions" in diarization_output:
            st.markdown(
                f"<span style='color:red;'>**Interruptions:**</span>"
                f"{diarization_output['interruptions']}</span>",\
                unsafe_allow_html=True)
        if "time_to_first_token" in diarization_output:
            st.markdown(
                f"<span style='color:green;'>**Time to First Token (TTFT):**</span>"
                f"{diarization_output['time_to_first_token']:.2f}s</span>",\
            unsafe_allow_html=True)
    else:
        st.markdown("Not selected")

    if st.session_state.get("diarization_status", "").startswith("✅"):
        st.success(st.session_state["diarization_status"])
    else:
        st.warning(st.session_state["diarization_status"])

# 3. Speaking Speed
st.subheader("⏩ Speaking Speed")
with st.expander("View Speaking Speed", expanded=True):
    st.markdown(st.session_state.get("speaking_speed_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("speaking_speed_status", "").startswith("✅"):
        st.success(st.session_state["speaking_speed_status"])
    else:
        st.warning(st.session_state["speaking_speed_status"])

# 4. PII Check
st.subheader("🔒 PII Check")
with st.expander("View PII Check", expanded=True):
    st.markdown(st.session_state.get("pii_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("pii_status", "").startswith("✅"):
        st.success(st.session_state["pii_status"])
    else:
        st.warning(st.session_state["pii_status"])

# 5. Profanity Check
st.subheader("🚫 Profanity Check")
with st.expander("View Profanity Check", expanded=True):
    st.markdown(st.session_state.get("profanity_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("profanity_status", "").startswith("✅"):
        st.success(st.session_state["profanity_status"])
    else:
        st.warning(st.session_state["profanity_status"])

# 6. Required Phrases
st.subheader("🔍 Required Phrases")
with st.expander("View Required Phrases", expanded=True):
    st.markdown(st.session_state.get("phrases_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("phrases_status", "").startswith("✅"):
        st.success(st.session_state["phrases_status"])
    else:
        st.warning(st.session_state["phrases_status"])

# 7. Sentiment Analysis
st.subheader("😊 Sentiment Analysis")
with st.expander("View Sentiment Analysis", expanded=True):
    st.markdown(st.session_state.get("sentiment_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("sentiment_status", "").startswith("✅"):
        st.success(st.session_state["sentiment_status"])
    else:
        st.warning(st.session_state["sentiment_status"])

# 8. Call Category
st.subheader("🏷️ Call Category")
with st.expander("View Call Category", expanded=True):
    st.markdown(st.session_state.get("category_output", "Not selected"),\
    unsafe_allow_html=True)
    if st.session_state.get("category_status", "").startswith("✅"):
        st.success(st.session_state["category_status"])
    else:
        st.warning(st.session_state["category_status"])

# 9. Summary Table
st.subheader("📊 Summary Table")
summary_output = st.session_state.get("summary_output", {})
if isinstance(summary_output, dict) and \
    "columns" in summary_output and "rows" in summary_output:
    st.table(summary_output["rows"])
else:
    st.markdown("Summary table will appear here...")

if st.session_state.get("summary_status", "").startswith("✅"):
    st.success(st.session_state["summary_status"])
else:
    st.warning(st.session_state["summary_status"])

# 10. Call Processing Status
st.subheader("✅ Call Processing Status")
with st.expander("View Call Processing Status", expanded=True):
    st.markdown(st.session_state.get("process_output", "Not selected"),
     unsafe_allow_html=True)
    if st.session_state.get("process_status", "").startswith("✅"):
        st.success(st.session_state["process_status"])
    else:
        st.warning(st.session_state["process_status"])
