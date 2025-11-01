"""
Service C3: Translation Service
Translates the story to multiple languages.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c3(message: PipelineMessage) -> PipelineMessage:
    """
    Translate story to other languages.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with translations
    """
    # Simulate processing time (varies - translation takes longer)
    time.sleep(random.uniform(0.25, 0.3))  # 250-300ms processing
    
    story = message.story_text or ""
    
    # Simple translation simulation using pattern replacement
    # (In real implementation, this would use a translation API)
    translations = {}
    
    # Simulate Spanish translation
    spanish_keywords = {
        "Once upon a time": "Había una vez",
        "in a world where": "en un mundo donde",
        "they discovered": "descubrieron",
        "journeyed to": "viajaron a",
        "encountered": "encontraron",
        "And so": "Y así",
        "forever": "para siempre",
        "adventure": "aventura",
        "discovery": "descubrimiento"
    }
    
    spanish_story = story
    for eng, esp in spanish_keywords.items():
        spanish_story = spanish_story.replace(eng, esp)
    
    translations["spanish"] = spanish_story
    
    # Simulate French translation
    french_keywords = {
        "Once upon a time": "Il était une fois",
        "in a world where": "dans un monde où",
        "they discovered": "ils ont découvert",
        "journeyed to": "voyagé vers",
        "encountered": "rencontré",
        "And so": "Et ainsi",
        "forever": "pour toujours",
        "adventure": "aventure",
        "discovery": "découverte"
    }
    
    french_story = story
    for eng, fr in french_keywords.items():
        french_story = french_story.replace(eng, fr)
    
    translations["french"] = french_story
    
    message.translations = translations
    
    return message


# Service function for pipeline
service_c3 = process_service_c3

