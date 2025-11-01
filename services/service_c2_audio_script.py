"""
Service C2: Audio Script Service
Creates narration script with dramatic pauses and emphasis markers.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c2(message: PipelineMessage) -> PipelineMessage:
    """
    Generate audio narration script from story with complex audio processing.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with audio_script data
    """
    story = message.story_text or ""
    analysis = message.analysis or {}
    words = story.split()
    
    # Phase 1: Audio timing analysis
    # Analyze sentence lengths for pause placement
    sentences = story.split('. ')
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    
    # Phase 2: Multiple-pass script generation
    script_lines = []
    emphasis_points = []
    pause_points = []
    
    # First pass: Identify emphasis candidates
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Calculate sentence importance (simplified)
        word_count = len(sentence.split())
        importance_score = 0
        
        # Simulate importance calculation with loops
        for word in sentence.split():
            importance_score += len(word)
            # Check for key words
            if any(kw in word.lower() for kw in ['discover', 'find', 'realize', 'understand']):
                importance_score += 5
        
        # Determine emphasis based on importance
        if importance_score > word_count * 3:
            emphasis_points.append(i)
    
    # Second pass: Generate script with markers
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        word_count = len(sentence.split())
        needs_pause = word_count > 15 or i % 3 == 0
        
        # Add appropriate markers
        if i in emphasis_points:
            script_lines.append(f"[EMPHASIS] {sentence} [PAUSE]")
            pause_points.append(i)
        elif i == len(sentences) - 1:
            script_lines.append(f"{sentence} [FADE_OUT]")
        elif needs_pause:
            script_lines.append(f"{sentence} [PAUSE]")
            pause_points.append(i)
        else:
            script_lines.append(sentence)
    
    narration_script = " ".join(script_lines)
    
    # Phase 3: Duration calculation with detailed analysis
    total_words = analysis.get("word_count", len(words))
    
    # Simulate reading speed calculation (multiple factors)
    speed_factors = []
    for factor in range(10):
        # Simulate factor calculation
        speed_factor = sum(i for i in range(20)) % 50 + 100
        speed_factors.append(speed_factor)
    
    avg_speed = sum(speed_factors) / len(speed_factors) if speed_factors else 150
    estimated_duration_minutes = round(total_words / avg_speed, 1)
    
    # Phase 4: Tone analysis with sentiment processing
    sentiment = analysis.get("sentiment", "neutral")
    tone_intensity = 0
    
    # Calculate tone intensity
    sentiment_words = {'positive': ['happy', 'joy', 'great'], 
                       'negative': ['sad', 'fear', 'dark']}
    relevant_words = sentiment_words.get(sentiment, [])
    
    for word in words:
        if any(sw in word.lower() for sw in relevant_words):
            tone_intensity += 1
    
    tone = sentiment
    if tone_intensity > len(words) / 10:
        tone += " (strong)"
    
    audio_script = {
        "narration": narration_script,
        "duration_estimate_minutes": estimated_duration_minutes,
        "duration_estimate_seconds": int(estimated_duration_minutes * 60),
        "word_count": total_words,
        "tone": tone,
        "emphasis_points": len(emphasis_points),
        "pause_points": len(pause_points),
        "sentence_count": len(sentences),
        "processing_passes": 4
    }
    
    message.audio_script = audio_script
    
    return message


# Service function for pipeline
service_c2 = process_service_c2

