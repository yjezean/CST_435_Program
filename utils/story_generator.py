"""
Story generation utilities using template-based approach.
"""
import random
from typing import Dict, List


class StoryGenerator:
    """Generates creative stories based on user prompts."""
    
    # Story templates
    OPENINGS = [
        "Once upon a time",
        "In a world where",
        "Deep in the heart of",
        "Long ago, in the realm of",
        "At the edge of the universe",
        "In a distant galaxy",
        "Many years ago",
        "In a land far, far away"
    ]
    
    ADVENTURE_THEMES = {
        "space": {
            "settings": ["space station", "distant planet", "asteroid field", "nebula", "alien world"],
            "characters": ["astronaut", "alien", "robot", "space explorer", "cosmic engineer"],
            "actions": ["discovered", "encountered", "explored", "journeyed to", "investigated"],
            "discoveries": ["ancient artifact", "mysterious signal", "new life form", "lost civilization", "cosmic secret"]
        },
        "fantasy": {
            "settings": ["enchanted forest", "ancient castle", "magical kingdom", "mystical realm", "hidden valley"],
            "characters": ["wizard", "dragon", "knight", "elf", "magical creature"],
            "actions": ["fought", "discovered", "sought", "encountered", "saved"],
            "discoveries": ["ancient magic", "hidden treasure", "forgotten prophecy", "secret power", "legendary artifact"]
        },
        "modern": {
            "settings": ["busy city", "quiet laboratory", "coastal town", "mountain retreat", "tech hub"],
            "characters": ["scientist", "detective", "entrepreneur", "artist", "researcher"],
            "actions": ["developed", "investigated", "created", "solved", "discovered"],
            "discoveries": ["breakthrough technology", "hidden truth", "creative solution", "ancient secret", "new perspective"]
        },
        "robots": {
            "settings": ["factory", "research lab", "space station", "smart city", "cyber world"],
            "characters": ["AI assistant", "robot companion", "cyborg", "engineer", "researcher"],
            "actions": ["programmed", "designed", "collaborated with", "learned from", "worked alongside"],
            "discoveries": ["new capability", "emotional intelligence", "creative solution", "friendship", "understanding"]
        }
    }
    
    MIDDLE_EVENTS = [
        "Along the way, they encountered challenges that tested their resolve.",
        "However, a mysterious obstacle appeared that changed everything.",
        "But their journey was not without unexpected surprises.",
        "Yet, what they found was far more remarkable than expected.",
        "Suddenly, they realized the true nature of their quest."
    ]
    
    CONFLICTS = [
        "They had to overcome their fears and work together.",
        "Time was running out, and decisions had to be made quickly.",
        "The stakes were higher than anyone had imagined.",
        "Old rivalries resurfaced, threatening to derail their mission.",
        "Nature itself seemed to conspire against their plans."
    ]
    
    RESOLUTIONS = [
        "In the end, they discovered that cooperation and understanding were the keys to success.",
        "Through perseverance and creativity, they found a way forward.",
        "The journey taught them valuable lessons about trust and friendship.",
        "With determination and teamwork, they achieved their goal.",
        "The experience transformed them in ways they never expected."
    ]
    
    ENDINGS = [
        "And so, their adventure became legend, inspiring future generations.",
        "The memory of this journey would stay with them forever.",
        "As the sun set, they knew they had found something precious.",
        "In that moment, everything fell into place.",
        "The story continues, but this chapter had come to a beautiful close."
    ]
    
    @classmethod
    def extract_theme(cls, prompt: str) -> str:
        """Extract theme from user prompt."""
        prompt_lower = prompt.lower()
        for theme in cls.ADVENTURE_THEMES.keys():
            if theme in prompt_lower:
                return theme
        # Default to first theme if none matches
        return random.choice(list(cls.ADVENTURE_THEMES.keys()))
    
    @classmethod
    def generate_story(cls, prompt: str, length: str = "medium") -> str:
        """
        Generate a story based on the prompt.
        
        Args:
            prompt: User's story prompt
            length: "short", "medium", or "long"
        """
        theme = cls.extract_theme(prompt)
        theme_data = cls.ADVENTURE_THEMES[theme]
        
        # Determine number of paragraphs
        if length == "short":
            num_paragraphs = 2
        elif length == "long":
            num_paragraphs = 5
        else:
            num_paragraphs = 3
        
        paragraphs = []
        
        # Opening paragraph
        opening = random.choice(cls.OPENINGS)
        setting = random.choice(theme_data["settings"])
        character = random.choice(theme_data["characters"])
        action = random.choice(theme_data["actions"])
        discovery = random.choice(theme_data["discoveries"])
        
        para1 = f"{opening}, there was a {character} who {action} {setting}. " \
                f"During their quest, they {action} a {discovery} that would change everything."
        paragraphs.append(para1)
        
        # Middle paragraphs
        if num_paragraphs >= 3:
            middle_event = random.choice(cls.MIDDLE_EVENTS)
            conflict = random.choice(cls.CONFLICTS)
            paragraphs.append(middle_event + " " + conflict)
        
        if num_paragraphs >= 4:
            resolution = random.choice(cls.RESOLUTIONS)
            paragraphs.append(resolution)
        
        # Closing paragraph
        ending = random.choice(cls.ENDINGS)
        paragraphs.append(ending)
        
        story = "\n\n".join(paragraphs)
        
        return story
    
    @classmethod
    def generate_with_characters(cls, prompt: str) -> Dict[str, any]:
        """
        Generate story with named characters.
        
        Returns:
            Dictionary with story text and metadata
        """
        theme = cls.extract_theme(prompt)
        story_text = cls.generate_story(prompt)
        
        # Extract or generate character names
        character_names = []
        theme_data = cls.ADVENTURE_THEMES[theme]
        if "robot" in prompt.lower() or "ai" in prompt.lower():
            character_names = ["Rover", "Aria", "Cortex"]
        elif "space" in prompt.lower():
            character_names = ["Commander Nova", "Stellar", "Cosmic"]
        elif "fantasy" in prompt.lower():
            character_names = ["Luna", "Thorn", "Ember"]
        else:
            character_names = ["Alex", "Morgan", "Casey"]
        
        return {
            "text": story_text,
            "characters": character_names[:2],  # Take first 2
            "theme": theme,
            "word_count": len(story_text.split())
        }

