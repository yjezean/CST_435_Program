"""
Service C2: Audio Script Service
Creates narration script with dramatic pauses and emphasis markers.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c2(message: PipelineMessage) -> PipelineMessage:
    """
    Generate audio narration script from story.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with audio_script data
    """
    # Simulate processing time (varies)
    time.sleep(random.uniform(0.15, 0.2))  # 150-200ms processing
    
    story = message.story_text or ""
    analysis = message.analysis or {}
    
    # Add dramatic pauses and emphasis
    script_lines = []
    sentences = story.split('. ')
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Add pauses at natural breaks
        if i == 0:
            # Opening sentence gets emphasis
            script_lines.append(f"[EMPHASIS] {sentence} [PAUSE]")
        elif i == len(sentences) - 1:
            # Closing sentence gets gentle fade
            script_lines.append(f"{sentence} [FADE_OUT]")
        elif i % 3 == 0:
            # Every third sentence gets a pause
            script_lines.append(f"{sentence} [PAUSE]")
        else:
            script_lines.append(sentence)
    
    narration_script = " ".join(script_lines)
    
    # Estimate duration (rough calculation: ~150 words per minute)
    word_count = analysis.get("word_count", len(story.split()))
    estimated_duration_minutes = round(word_count / 150, 1)
    
    audio_script = {
        "narration": narration_script,
        "duration_estimate_minutes": estimated_duration_minutes,
        "duration_estimate_seconds": int(estimated_duration_minutes * 60),
        "word_count": word_count,
        "tone": message.analysis.get("sentiment", "neutral") if message.analysis else "neutral"
    }
    
    message.audio_script = audio_script
    
    return message


# Service function for pipeline
service_c2 = process_service_c2

