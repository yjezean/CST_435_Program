"""
Service B: Story Analyzer Service
Analyzes the generated story for sentiment, keywords, and statistics.
"""
import time
from core.message import PipelineMessage
from utils.text_analyzer import TextAnalyzer


def process_service_b(message: PipelineMessage) -> PipelineMessage:
    """
    Analyze the story from Service A.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with analysis data
    """
    if not message.story_text:
        raise ValueError("Story text required for analysis")
    
    # Simulate processing time
    time.sleep(0.1)  # 100ms processing simulation
    
    # Get known characters from metadata if available
    known_characters = message.metadata.get("characters", [])
    
    # Perform analysis
    analysis = TextAnalyzer.analyze(message.story_text, known_characters)
    
    # Update message
    message.analysis = analysis
    
    return message


# Service function for pipeline
service_b = process_service_b

