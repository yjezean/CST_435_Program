"""
Service C1: Image Concept Generator Service
Creates visual concept descriptions based on the story.
"""
import time
import random
from core.message import PipelineMessage


def process_service_c1(message: PipelineMessage) -> PipelineMessage:
    """
    Generate image concept from story with complex visual analysis.
    
    Args:
        message: Pipeline message with story_text and analysis
        
    Returns:
        Updated message with image_concept data
    """
    story = message.story_text or ""
    analysis = message.analysis or {}
    theme = message.metadata.get("theme", "fantasy")
    keywords = analysis.get("keywords", [])
    
    # Phase 1: Visual element extraction with loops
    visual_elements = []
    story_words = story.split()
    element_count = 0
    for word in story_words:
        # Simulate visual element detection
        if len(word) > 4:
            element_count += 1
            # Simulate processing
            _ = sum(ord(c) for c in word.lower()) % 100
    
    # Phase 2: Color analysis (multiple iterations)
    color_analysis_iterations = 15
    color_scores = {}
    sentiment = analysis.get("sentiment", "neutral")
    
    color_palettes = {
        "positive": ["bright blue", "golden yellow", "emerald green", "sky blue", "sunset orange"],
        "negative": ["deep purple", "dark gray", "crimson red", "midnight blue", "storm gray"],
        "neutral": ["silver", "steel blue", "charcoal", "ocean blue", "mist gray"]
    }
    
    available_colors = color_palettes.get(sentiment, color_palettes["neutral"])
    
    # Simulate color scoring for each color
    for iteration in range(color_analysis_iterations):
        for color in available_colors:
            # Simulate color compatibility scoring
            score = sum(ord(c) for c in color) % 100
            color_scores[color] = color_scores.get(color, 0) + score
    
    # Select top colors based on scores
    sorted_colors = sorted(color_scores.items(), key=lambda x: x[1], reverse=True)
    colors = [color for color, _ in sorted_colors[:3]]
    
    # Phase 3: Scene composition generation
    scenes = {
        "space": ["futuristic space station", "distant planet surface", "cosmic nebula", "asteroid field"],
        "fantasy": ["enchanted forest", "mystical castle", "magical realm", "ancient ruins"],
        "modern": ["urban cityscape", "coastal town", "mountain vista", "tech hub"],
        "robots": ["futuristic factory", "smart city", "research laboratory", "cyber space"]
    }
    
    # Simulate scene selection process
    scene_candidates = scenes.get(theme, scenes["fantasy"])
    scene_scores = {}
    for scene in scene_candidates:
        # Simulate scoring
        for word in keywords:
            if word.lower() in scene.lower():
                scene_scores[scene] = scene_scores.get(scene, 0) + 10
    
    scene = max(scene_scores.items(), key=lambda x: x[1])[0] if scene_scores else random.choice(scene_candidates)
    
    # Phase 4: Mood calculation with multiple factors
    mood_factors = []
    for factor in range(5):
        # Simulate mood factor calculation
        factor_score = sum(i * factor for i in range(20))
        mood_factors.append(factor_score)
    
    avg_mood_score = sum(mood_factors) / len(mood_factors) if mood_factors else 50
    mood = "hopeful adventure" if sentiment == "positive" else "mysterious journey" if sentiment == "negative" else "contemplative exploration"
    
    # Phase 5: Style determination with processing
    style_options = ["digital art", "fantasy illustration", "realistic painting", "abstract design"]
    style_scores = {}
    for style in style_options:
        # Simulate style compatibility check
        compatibility = 0
        for char in style:
            compatibility += ord(char) % 50
        style_scores[style] = compatibility
    
    selected_style = max(style_scores.items(), key=lambda x: x[1])[0] if style_scores else "digital art"
    
    image_concept = {
        "scene_description": scene,
        "color_palette": colors,
        "mood": mood,
        "key_elements": keywords[:3] if keywords else ["adventure", "discovery"],
        "style": selected_style,
        "visual_elements_detected": element_count,
        "color_analysis_iterations": color_analysis_iterations
    }
    
    message.image_concept = image_concept
    
    return message


# Service function for pipeline
service_c1 = process_service_c1

