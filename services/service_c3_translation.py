"""
Service C3: Translation Service
Translates the story to multiple languages.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c3(message: PipelineMessage) -> PipelineMessage:
    """
    Translate story to other languages with complex translation processing.
    
    Args:
        message: Pipeline message with story_text
        
    Returns:
        Updated message with translations
    """
    story = message.story_text or ""
    words = story.split()
    
    translations = {}
    target_languages = ["spanish", "french"]
    
    # Phase 1: Pre-translation analysis
    # Analyze text complexity
    word_lengths = [len(word) for word in words]
    avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
    complexity_score = avg_word_length * len(words)
    
    # Phase 2: Translation dictionary expansion
    # Build comprehensive translation dictionaries
    spanish_keywords = {
        "Once upon a time": "Había una vez",
        "in a world where": "en un mundo donde",
        "they discovered": "descubrieron",
        "journeyed to": "viajaron a",
        "encountered": "encontraron",
        "And so": "Y así",
        "forever": "para siempre",
        "adventure": "aventura",
        "discovery": "descubrimiento",
        "space": "espacio",
        "robot": "robot",
        "story": "historia"
    }
    
    french_keywords = {
        "Once upon a time": "Il était une fois",
        "in a world where": "dans un monde où",
        "they discovered": "ils ont découvert",
        "journeyed to": "voyagé vers",
        "encountered": "rencontré",
        "And so": "Et ainsi",
        "forever": "pour toujours",
        "adventure": "aventure",
        "discovery": "découverte",
        "space": "espace",
        "robot": "robot",
        "story": "histoire"
    }
    
    # Phase 3: Multi-pass translation for each language
    for lang in target_languages:
        if lang == "spanish":
            keyword_dict = spanish_keywords
        else:
            keyword_dict = french_keywords
        
        # First pass: Direct phrase replacement
        translated_text = story
        replacement_count = 0
        for eng_phrase, translation in keyword_dict.items():
            if eng_phrase in translated_text:
                translated_text = translated_text.replace(eng_phrase, translation)
                replacement_count += 1
        
        # Second pass: Word-level translation (simulated)
        # Analyze remaining untranslated words
        translated_words = translated_text.split()
        untranslated_words = []
        for word in words:
            if word not in keyword_dict:
                clean_word = word.lower().strip('.,!?;:()[]{}"\'')
                if clean_word not in [kw.lower() for kw in keyword_dict.keys()]:
                    untranslated_words.append(word)
        
        # Phase 4: Translation quality scoring
        translation_scores = []
        for iteration in range(5):
            # Simulate translation quality assessment
            quality_score = 0
            for word in translated_words:
                # Simulate quality calculation
                word_score = sum(ord(c) % 10 for c in word.lower())
                quality_score += word_score
            translation_scores.append(quality_score)
        
        avg_quality = sum(translation_scores) / len(translation_scores) if translation_scores else 0
        
        # Phase 5: Post-translation processing
        # Simulate grammar checking and refinement
        refinement_passes = 3
        for pass_num in range(refinement_passes):
            # Simulate refinement computations
            _ = sum(i * len(translated_words) * pass_num for i in range(20))
        
        # Store translation with metadata
        translations[lang] = translated_text
        message.metadata[f"{lang}_translation_metadata"] = {
            "replacement_count": replacement_count,
            "untranslated_words": len(untranslated_words),
            "quality_score": round(avg_quality, 2),
            "refinement_passes": refinement_passes
        }
    
    message.translations = translations
    
    return message


# Service function for pipeline
service_c3 = process_service_c3

