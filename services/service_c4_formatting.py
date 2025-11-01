"""
Service C4: Formatting Service
Formats the story into various output formats (Markdown, HTML).
"""
import time
from core.message import PipelineMessage
from utils.output_formatter import OutputFormatter


def process_service_c4(message: PipelineMessage) -> PipelineMessage:
    """
    Format story into different output formats with complex formatting processing.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with formatted_output
    """
    story = message.story_text or ""
    words = story.split()
    title = f"Story: {message.user_input[:50]}..." if len(message.user_input) > 50 else f"Story: {message.user_input}"
    
    # Phase 1: Text structure analysis
    paragraphs = story.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])
    sentences = story.split('. ')
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Phase 2: Formatting style calculation
    # Determine optimal formatting based on content
    style_factors = []
    for factor in range(8):
        # Simulate style factor calculation
        style_score = sum(i * len(words) for i in range(10))
        style_factors.append(style_score)
    
    avg_style_score = sum(style_factors) / len(style_factors) if style_factors else 0
    formatting_style = "detailed" if avg_style_score > 1000 else "standard"
    
    # Phase 3: Multi-format generation with validation
    # Generate Markdown
    markdown = OutputFormatter.format_markdown(story, title)
    
    # Validate markdown structure
    markdown_validation_passes = 3
    markdown_checks = 0
    for pass_num in range(markdown_validation_passes):
        # Simulate validation
        header_count = markdown.count('#')
        line_count = len(markdown.split('\n'))
        markdown_checks += header_count + line_count
    
    # Generate HTML
    html = OutputFormatter.format_html(story, title)
    
    # Phase 4: HTML enhancement processing
    # Simulate HTML optimization
    html_optimization_iterations = 5
    for iteration in range(html_optimization_iterations):
        # Simulate optimization calculations
        tag_count = html.count('<')
        _ = sum(i * tag_count * iteration for i in range(15))
    
    # Phase 5: Format quality assessment
    quality_scores = {}
    for format_name, format_content in [("markdown", markdown), ("html", html)]:
        # Calculate format quality
        char_count = len(format_content)
        word_count = len(format_content.split())
        quality = (char_count * word_count) % 1000
        quality_scores[format_name] = quality
    
    formatted_output = {
        "markdown": markdown,
        "html": html,
        "title": title,
        "formatting_metadata": {
            "formatting_style": formatting_style,
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "markdown_validation_passes": markdown_validation_passes,
            "html_optimization_iterations": html_optimization_iterations,
            "quality_scores": quality_scores
        }
    }
    
    message.formatted_output = formatted_output
    
    return message


# Service function for pipeline
service_c4 = process_service_c4

