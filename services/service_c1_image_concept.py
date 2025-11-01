"""
Service C1: Image Concept Generator Service
Creates visual concept descriptions based on the story.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c1(message: PipelineMessage) -> PipelineMessage:
    """
    Generate image concept from story.
    
    Args:
        message: Pipeline message with story_text and analysis
        
    Returns:
        Updated message with image_concept data
    """
    # Simulate processing time (varies)
    time.sleep(random.uniform(0.1, 0.15))  # 100-150ms processing
    
    story = message.story_text or ""
    analysis = message.analysis or {}
    theme = message.metadata.get("theme", "fantasy")
    keywords = analysis.get("keywords", [])
    
    # Generate scene description based on theme
    scenes = {
        "space": ["futuristic space station", "distant planet surface", "cosmic nebula", "asteroid field"],
        "fantasy": ["enchanted forest", "mystical castle", "magical realm", "ancient ruins"],
        "modern": ["urban cityscape", "coastal town", "mountain vista", "tech hub"],
        "robots": ["futuristic factory", "smart city", "research laboratory", "cyber space"]
    }
    
    scene = random.choice(scenes.get(theme, scenes["fantasy"]))
    
    # Color palettes based on sentiment
    sentiment = analysis.get("sentiment", "neutral")
    color_palettes = {
        "positive": ["bright blue", "golden yellow", "emerald green", "sky blue"],
        "negative": ["deep purple", "dark gray", "crimson red", "midnight blue"],
        "neutral": ["silver", "steel blue", "charcoal", "ocean blue"]
    }
    
    colors = random.sample(color_palettes.get(sentiment, color_palettes["neutral"]), 3)
    mood = "hopeful adventure" if sentiment == "positive" else "mysterious journey" if sentiment == "negative" else "contemplative exploration"
    
    image_concept = {
        "scene_description": scene,
        "color_palette": colors,
        "mood": mood,
        "key_elements": keywords[:3] if keywords else ["adventure", "discovery"],
        "style": "digital art" if theme == "space" or theme == "robots" else "fantasy illustration"
    }
    
    message.image_concept = image_concept
    
    return message


# Service function for pipeline
service_c1 = process_service_c1

