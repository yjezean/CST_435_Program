"""
Service B: Story Analyzer Service
Analyzes the generated story for sentiment, keywords, and statistics.
"""
import time
from core.message import PipelineMessage
from utils.text_analyzer import TextAnalyzer


def process_service_b(message: PipelineMessage) -> PipelineMessage:
    """
    Analyze the story from Service A with comprehensive processing.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with analysis data
    """
    if not message.story_text:
        raise ValueError("Story text required for analysis")
    
    story_text = message.story_text
    words = story_text.split()
    
    # Phase 1: Multi-pass text processing
    # First pass: Word frequency analysis
    word_frequency = {}
    for word in words:
        clean_word = word.lower().strip('.,!?;:()[]{}"\'').strip()
        if len(clean_word) > 0:
            word_frequency[clean_word] = word_frequency.get(clean_word, 0) + 1
    
    # Second pass: Character analysis with loops
    character_count = {}
    for char in story_text.lower():
        if char.isalpha():
            character_count[char] = character_count.get(char, 0) + 1
    
    # Phase 2: Statistical computations
    # Calculate various statistics
    total_chars = sum(len(word) for word in words)
    avg_word_length = total_chars / len(words) if words else 0
    
    # Phase 3: Pattern detection (simulated with loops)
    pattern_searches = 10
    patterns_found = []
    for pattern_id in range(pattern_searches):
        # Simulate pattern matching
        matches = 0
        search_term = f"pattern{pattern_id}"
        for word in words:
            if search_term[:3] in word.lower():
                matches += 1
        if matches > 0:
            patterns_found.append(f"pattern_{pattern_id}")
    
    # Phase 4: Sentiment analysis (multiple passes)
    sentiment_passes = 3
    sentiment_scores = []
    for pass_num in range(sentiment_passes):
        # Simulate sentiment calculation
        positive_count = sum(1 for word in words if any(p in word.lower() for p in ['happy', 'joy', 'love', 'great']))
        negative_count = sum(1 for word in words if any(n in word.lower() for n in ['sad', 'fear', 'dark', 'lost']))
        score = (positive_count - negative_count) / max(len(words), 1)
        sentiment_scores.append(score)
    
    # Phase 5: Keyword extraction with ranking
    # Calculate TF-like scores (simplified)
    keyword_scores = {}
    for word, freq in word_frequency.items():
        if len(word) > 3:  # Filter short words
            # Simple scoring
            score = freq * len(word)
            keyword_scores[word] = score
    
    # Get known characters from metadata if available
    known_characters = message.metadata.get("characters", [])
    
    # Perform standard analysis (calls the utility)
    analysis = TextAnalyzer.analyze(story_text, known_characters)
    
    # Enhance with computed statistics
    analysis["processing_metadata"] = {
        "word_frequency_analysis": len(word_frequency),
        "character_analysis_count": len(character_count),
        "pattern_searches_performed": pattern_searches,
        "patterns_found": len(patterns_found),
        "sentiment_passes": sentiment_passes,
        "avg_word_length_calculated": round(avg_word_length, 2)
    }
    
    # Update message
    message.analysis = analysis
    
    return message


# Service function for pipeline
service_b = process_service_b

