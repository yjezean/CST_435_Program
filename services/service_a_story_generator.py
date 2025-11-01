"""
Service A: Story Generator Service
Generates a creative story based on user prompt.
"""
import time
from core.message import PipelineMessage
from utils.story_generator import StoryGenerator


def process_service_a(message: PipelineMessage) -> PipelineMessage:
    """
    Generate story from user input.
    
    Args:
        message: Pipeline message with user_input
        
    Returns:
        Updated message with story_text
    """
    # Simulate processing time
    time.sleep(0.2)  # 200ms processing simulation
    
    # Generate story
    story_data = StoryGenerator.generate_with_characters(message.user_input)
    
    # Update message
    message.story_text = story_data["text"]
    message.metadata["characters"] = story_data["characters"]
    message.metadata["theme"] = story_data["theme"]
    
    return message


# Service function for pipeline
service_a = process_service_a

