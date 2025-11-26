"""
Service D: Final Aggregator Service
Combines all results from the pipeline into a final package.
"""
import time
import json
from core.message import PipelineMessage
import os
import json
import threading
from core import rpc as _rpc
from core.timestamp_tracker import TimestampTracker as _TimestampTracker


def process_service_d(message: PipelineMessage) -> PipelineMessage:
    """
    Aggregate all results into final package with comprehensive validation.
    
    Args:
        message: Pipeline message with all service results
        
    Returns:
        Updated message with complete package
    """
    # Phase 1: Multi-pass validation
    validation_results = {
        "story_text": message.story_text is not None,
        "analysis": message.analysis is not None,
        "image_concept": message.image_concept is not None,
        "audio_script": message.audio_script is not None,
        "translations": message.translations is not None,
        "formatted_output": message.formatted_output is not None,
    }
    
    # Validate each component in detail
    validation_passes = 3
    validation_details = {}
    
    for pass_num in range(validation_passes):
        for component, is_present in validation_results.items():
            if component not in validation_details:
                validation_details[component] = []
            
            if is_present:
                # Simulate detailed validation
                validation_score = 0
                # Check component quality
                if component == "story_text" and message.story_text:
                    validation_score = len(message.story_text.split())
                elif component == "analysis" and message.analysis:
                    validation_score = len(message.analysis)
                elif component == "image_concept" and message.image_concept:
                    validation_score = len(message.image_concept)
                elif component == "audio_script" and message.audio_script:
                    validation_score = len(str(message.audio_script))
                elif component == "translations" and message.translations:
                    validation_score = len(message.translations)
                elif component == "formatted_output" and message.formatted_output:
                    validation_score = len(message.formatted_output)
                
                validation_details[component].append(validation_score)
    
    # Phase 2: Cross-component consistency checking
    consistency_checks = 5
    consistency_scores = []
    for check in range(consistency_checks):
        # Simulate cross-component validation
        score = 0
        if message.story_text and message.analysis:
            # Check if analysis matches story
            story_words = len(message.story_text.split())
            analysis_words = message.analysis.get("word_count", 0)
            if abs(story_words - analysis_words) < 10:
                score += 10
        
        if message.story_text and message.translations:
            # Check translation completeness
            score += 5
        
        consistency_scores.append(score)
    
    avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
    
    # Phase 3: Data aggregation and statistics calculation
    all_complete = all(validation_results.values())
    
    # Calculate comprehensive statistics
    component_sizes = {}
    for component in validation_results.keys():
        if validation_results[component]:
            # Calculate component data size
            size = 0
            if component == "story_text":
                size = len(message.story_text) if message.story_text else 0
            elif component == "analysis":
                size = len(str(message.analysis)) if message.analysis else 0
            elif component == "image_concept":
                size = len(str(message.image_concept)) if message.image_concept else 0
            elif component == "audio_script":
                size = len(str(message.audio_script)) if message.audio_script else 0
            elif component == "translations":
                size = len(str(message.translations)) if message.translations else 0
            elif component == "formatted_output":
                size = len(str(message.formatted_output)) if message.formatted_output else 0
            
            component_sizes[component] = size
    
    total_data_size = sum(component_sizes.values())
    
    # Phase 4: Summary generation with multiple iterations
    summary_iterations = 4
    for iteration in range(summary_iterations):
        # Simulate summary generation processing
        _ = sum(i * total_data_size * iteration for i in range(25))
    
    summary = {
        "pipeline_complete": all_complete,
        "components_received": sum(validation_results.values()),
        "total_components": len(validation_results),
        "validation": validation_results,
        "validation_details": {k: round(sum(v)/len(v), 2) if v else 0 
                                for k, v in validation_details.items()},
        "consistency_score": round(avg_consistency, 2),
        "total_data_size": total_data_size,
        "validation_passes": validation_passes,
        "consistency_checks": consistency_checks
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


def _rpc_handler(params: dict) -> dict:
    pm = PipelineMessage.from_dict(params)
    tracker = _TimestampTracker()
    tracker.mark_received(pm, "service_d_aggregator")
    tracker.mark_started(pm, "service_d_aggregator")
    try:
        result = process_service_d(pm)
        tracker.mark_completed(result, "service_d_aggregator")
        return result.to_dict()
    except Exception:
        tracker.mark_completed(pm, "service_d_aggregator")
        raise


if __name__ == "__main__":
    mode = os.environ.get("PIPELINE_MODE", "rpc").lower()
    port = int(os.environ.get("PORT", os.environ.get("RPC_PORT", os.environ.get("SERVICE_PORT", "50058"))))
    host = os.environ.get("HOST", "0.0.0.0")
    if mode == "grpc":
        from core import grpc_server as _grpc_server
        
        print(f"Starting gRPC server for service_d on {host}:{port}")
        def _grpc_handler(pm: PipelineMessage) -> PipelineMessage:
            tracker = _TimestampTracker()
            tracker.mark_received(pm, "service_d_aggregator")
            tracker.mark_started(pm, "service_d_aggregator")
            try:
                result = process_service_d(pm)
                tracker.mark_completed(result, "service_d_aggregator")
                return result
            except Exception:
                tracker.mark_completed(pm, "service_d_aggregator")
                raise

        server = _grpc_server.serve(_grpc_handler, host=host, port=port)
    else:
        print(f"Starting RPC server for service_d on {host}:{port}")
        server = _rpc.serve(_rpc_handler, host=host, port=port)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down server")

