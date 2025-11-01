"""
Service C: Parallel Processing Hub
Coordinates parallel execution of multiple services (C1, C2, C3, C4).
"""
import time
import concurrent.futures
from typing import List
from core.message import PipelineMessage
from core.timestamp_tracker import TimestampTracker
from services.service_c1_image_concept import process_service_c1
from services.service_c2_audio_script import process_service_c2
from services.service_c3_translation import process_service_c3
from services.service_c4_formatting import process_service_c4


def process_service_c(message: PipelineMessage) -> PipelineMessage:
    """
    Execute parallel services (C1, C2, C3, C4) simultaneously.
    
    Args:
        message: Pipeline message with story_text and analysis
        
    Returns:
        Updated message with results from all parallel services
    """
    tracker = TimestampTracker()
    
    # Mark parallel hub start
    tracker.mark_started(message, "service_c_parallel_hub")
    
    # Define parallel service functions with their names
    parallel_services = [
        ("service_c1_image_concept", process_service_c1),
        ("service_c2_audio_script", process_service_c2),
        ("service_c3_translation", process_service_c3),
        ("service_c4_formatting", process_service_c4),
    ]
    
    # Execute all services in parallel
    def execute_with_tracking(service_name, service_func, msg):
        """Execute a service with timestamp tracking."""
        tracker.mark_received(msg, service_name)
        tracker.mark_started(msg, service_name)
        result = service_func(msg)
        tracker.mark_completed(result, service_name)
        return service_name, result
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks with tracking
        futures = {
            executor.submit(execute_with_tracking, name, func, message): name
            for name, func in parallel_services
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                service_name, result_message = future.result()
                # Update message with results from this service
                if result_message.image_concept:
                    message.image_concept = result_message.image_concept
                if result_message.audio_script:
                    message.audio_script = result_message.audio_script
                if result_message.translations:
                    message.translations = result_message.translations
                if result_message.formatted_output:
                    message.formatted_output = result_message.formatted_output
                # Merge timestamps
                for ts_name, ts_record in result_message.timestamps.items():
                    if ts_name not in message.timestamps:
                        message.timestamps[ts_name] = ts_record
            except Exception as e:
                print(f"Error in parallel service: {e}")
    
    # Mark parallel hub completion
    tracker.mark_completed(message, "service_c_parallel_hub")
    
    return message


# Service function for pipeline
service_c = process_service_c

