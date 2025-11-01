"""
Service D: Final Aggregator Service
Combines all results from the pipeline into a final package.
"""
import time
import json
from core.message import PipelineMessage


def process_service_d(message: PipelineMessage) -> PipelineMessage:
    """
    Aggregate all results into final package.
    
    Args:
        message: Pipeline message with all service results
        
    Returns:
        Updated message with complete package
    """
    # Simulate processing time
    time.sleep(0.05)  # 50ms processing
    
    # Validate that we have all required components
    validation_results = {
        "story_text": message.story_text is not None,
        "analysis": message.analysis is not None,
        "image_concept": message.image_concept is not None,
        "audio_script": message.audio_script is not None,
        "translations": message.translations is not None,
        "formatted_output": message.formatted_output is not None,
    }
    
    all_complete = all(validation_results.values())
    
    # Create summary statistics
    summary = {
        "pipeline_complete": all_complete,
        "components_received": sum(validation_results.values()),
        "total_components": len(validation_results),
        "validation": validation_results
    }
    
    # Add summary to metadata
    message.metadata["summary"] = summary
    
    # Calculate statistics
    if message.analysis:
        message.metadata["statistics"] = {
            "word_count": message.analysis.get("word_count", 0),
            "sentence_count": message.analysis.get("sentence_count", 0),
            "paragraph_count": message.analysis.get("paragraph_count", 0),
            "sentiment": message.analysis.get("sentiment", "unknown"),
            "translation_count": len(message.translations) if message.translations else 0,
            "formats_available": list(message.formatted_output.keys()) if message.formatted_output else []
        }
    
    return message


# Service function for pipeline
service_d = process_service_d

