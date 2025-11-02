"""
Service A: Story Generator Service
Generates a creative story based on user prompt.
"""
import time
from core.message import PipelineMessage
from utils.story_generator import StoryGenerator
import os
import json
import threading
from core import rpc as _rpc
from core.timestamp_tracker import TimestampTracker as _TimestampTracker


def process_service_a(message: PipelineMessage) -> PipelineMessage:
    """
    Generate story from user input with complex processing simulation.
    
    Args:
        message: Pipeline message with user_input
        
    Returns:
        Updated message with story_text
    """
    # Simulate complex story generation process
    # Multiple iterations to refine the story
    
    # Phase 1: Analyze prompt and generate initial draft
    prompt_words = message.user_input.split()
    word_count = len(prompt_words)
    
    # Simulate prompt analysis with loops
    theme_score = 0
    for word in prompt_words:
        # Simple scoring computation
        for char in word.lower():
            theme_score += ord(char) % 10
    
    # Phase 2: Generate multiple story variants (simulated)
    variant_count = max(3, word_count // 2)
    for variant in range(variant_count):
        # Simulate variant generation with computation
        _ = sum(i * i for i in range(100))  # Simulate processing work
    
    # Phase 3: Select and refine best variant
    # Simulate refinement process
    refinement_passes = 3
    for pass_num in range(refinement_passes):
        # Simulate refinement computations
        _ = sum(i * variant_count * pass_num for i in range(50))
    
    # Generate actual story
    story_data = StoryGenerator.generate_with_characters(message.user_input)
    
    # Phase 4: Post-processing (word count validation, structure check)
    story_words = story_data["text"].split()
    # Simulate validation loops
    validation_checks = 5
    for check in range(validation_checks):
        # Count words multiple times (simulating validation)
        word_freq = {}
        for word in story_words:
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    # Update message
    message.story_text = story_data["text"]
    message.metadata["characters"] = story_data["characters"]
    message.metadata["theme"] = story_data["theme"]
    message.metadata["generation_metadata"] = {
        "variants_generated": variant_count,
        "refinement_passes": refinement_passes,
        "validation_checks": validation_checks
    }
    
    return message


# Service function for pipeline
service_a = process_service_a


def _rpc_handler(params: dict) -> dict:
    """RPC handler wrapper for this service.

    Expects params to be a PipelineMessage-like dict. Returns message.to_dict().
    """
    pm = PipelineMessage.from_dict(params)
    tracker = _TimestampTracker()
    tracker.mark_received(pm, "service_a_story_generator")
    tracker.mark_started(pm, "service_a_story_generator")
    try:
        result = process_service_a(pm)
        tracker.mark_completed(result, "service_a_story_generator")
        return result.to_dict()
    except Exception as e:
        tracker.mark_completed(pm, "service_a_story_generator")
        raise


if __name__ == "__main__":
    # Read mode and port from environment
    mode = os.environ.get("PIPELINE_MODE", "rpc").lower()
    port = int(os.environ.get("PORT", os.environ.get("RPC_PORT", os.environ.get("SERVICE_PORT", "50051"))))
    host = os.environ.get("HOST", "0.0.0.0")
    if mode == "grpc":
        from core import grpc_server as _grpc_server

        print(f"Starting gRPC server for service_a on {host}:{port}")
        def _grpc_handler(pm: PipelineMessage) -> PipelineMessage:
            tracker = _TimestampTracker()
            tracker.mark_received(pm, "service_a_story_generator")
            tracker.mark_started(pm, "service_a_story_generator")
            try:
                result = process_service_a(pm)
                tracker.mark_completed(result, "service_a_story_generator")
                return result
            except Exception:
                tracker.mark_completed(pm, "service_a_story_generator")
                raise

        server = _grpc_server.serve(_grpc_handler, host=host, port=port)
    else:
        print(f"Starting RPC server for service_a on {host}:{port}")
        server = _rpc.serve(_rpc_handler, host=host, port=port)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down server")

