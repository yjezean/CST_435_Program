"""
Text analysis utilities for story processing.
"""
import re
from typing import Dict, List
from collections import Counter


class TextAnalyzer:
    """Analyzes text for sentiment, keywords, and statistics."""
    
    # Simple sentiment word lists (can be expanded)
    POSITIVE_WORDS = {
        "happy", "joy", "success", "love", "beautiful", "wonderful", "amazing",
        "fantastic", "brilliant", "delighted", "pleased", "excellent", "great",
        "good", "peaceful", "harmony", "cooperation", "friendship", "triumph",
        "victory", "discovery", "hope", "bright", "inspiring", "heroic"
    }
    
    NEGATIVE_WORDS = {
        "sad", "fear", "danger", "evil", "dark", "terrible", "awful",
        "horrible", "difficult", "struggle", "conflict", "failure", "lost",
        "defeat", "crisis", "threat", "worried", "anxious", "trouble"
    }
    
    NEUTRAL_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "can"
    }
    
    @classmethod
    def count_words(cls, text: str) -> int:
        """Count words in text."""
        words = text.split()
        return len(words)
    
    @classmethod
    def count_sentences(cls, text: str) -> int:
        """Count sentences in text."""
        # Simple sentence counting by punctuation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    @classmethod
    def count_paragraphs(cls, text: str) -> int:
        """Count paragraphs in text."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return len(paragraphs)
    
    @classmethod
    def analyze_sentiment(cls, text: str) -> str:
        """
        Analyze sentiment of text.
        Returns: "positive", "negative", or "neutral"
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in cls.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in cls.NEGATIVE_WORDS)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"
    
    @classmethod
    def extract_keywords(cls, text: str, top_n: int = 5) -> List[str]:
        """
        Extract top keywords from text.
        Returns list of most frequent meaningful words.
        """
        # Remove punctuation and convert to lowercase
        text_clean = re.sub(r'[^\w\s]', '', text.lower())
        words = text_clean.split()
        
        # Filter out common words
        meaningful_words = [
            word for word in words 
            if word not in cls.NEUTRAL_WORDS 
            and len(word) > 3  # Filter short words
        ]
        
        # Count frequency
        word_freq = Counter(meaningful_words)
        
        # Get top N
        top_keywords = [word for word, count in word_freq.most_common(top_n)]
        
        return top_keywords
    
    @classmethod
    def extract_characters(cls, text: str, known_characters: List[str] = None) -> List[str]:
        """
        Extract character names or references.
        Can use known characters list if provided.
        """
        if known_characters:
            found_characters = []
            text_lower = text.lower()
            for char in known_characters:
                if char.lower() in text_lower:
                    found_characters.append(char)
            return found_characters
        
        # Simple extraction: capitalized words that appear multiple times
        words = text.split()
        capitalized_words = [w.strip('.,!?;:') for w in words if w and w[0].isupper()]
        word_freq = Counter(capitalized_words)
        
        # Characters are likely to be repeated capitalized words (excluding first word of sentences)
        potential_chars = [word for word, count in word_freq.items() 
                          if count > 1 and word not in ['The', 'A', 'An', 'This', 'That', 'There']]
        
        return potential_chars[:5]  # Return top 5
    
    @classmethod
    def calculate_avg_word_length(cls, text: str) -> float:
        """Calculate average word length."""
        words = text.split()
        if not words:
            return 0.0
        total_length = sum(len(word.strip('.,!?;:')) for word in words)
        return round(total_length / len(words), 2)
    
    @classmethod
    def analyze(cls, text: str, known_characters: List[str] = None) -> Dict[str, any]:
        """
        Perform comprehensive text analysis.
        
        Returns:
            Dictionary with analysis results
        """
        return {
            "word_count": cls.count_words(text),
            "sentence_count": cls.count_sentences(text),
            "paragraph_count": cls.count_paragraphs(text),
            "sentiment": cls.analyze_sentiment(text),
            "keywords": cls.extract_keywords(text),
            "characters": cls.extract_characters(text, known_characters),
            "avg_word_length": cls.calculate_avg_word_length(text)
        }

