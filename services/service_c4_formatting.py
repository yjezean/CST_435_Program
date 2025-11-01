"""
Service C4: Formatting Service
Formats the story into various output formats (Markdown, HTML).
"""
import time
from core.message import PipelineMessage
from utils.output_formatter import OutputFormatter


def process_service_c4(message: PipelineMessage) -> PipelineMessage:
    """
    Format story into different output formats.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with formatted_output
    """
    # Simulate processing time
    time.sleep(0.05)  # 50ms processing
    
    story = message.story_text or ""
    title = f"Story: {message.user_input[:50]}..." if len(message.user_input) > 50 else f"Story: {message.user_input}"
    
    # Generate formatted outputs
    markdown = OutputFormatter.format_markdown(story, title)
    html = OutputFormatter.format_html(story, title)
    
    formatted_output = {
        "markdown": markdown,
        "html": html,
        "title": title
    }
    
    message.formatted_output = formatted_output
    
    return message


# Service function for pipeline
service_c4 = process_service_c4

