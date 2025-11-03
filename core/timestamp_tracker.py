"""
Timestamp tracking and display utilities for pipeline execution.
"""
import time
from typing import Dict, Optional
from datetime import datetime
from core.message import PipelineMessage, TimestampRecord


class TimestampTracker:
    """Utility class for tracking and displaying service execution times."""
    
    @staticmethod
    def mark_received(message: PipelineMessage, service_name: str) -> TimestampRecord:
        """Mark when a service receives a request."""
        ts = message.add_timestamp(service_name)
        ts.received_time = time.time()
        return ts
    
    @staticmethod
    def mark_started(message: PipelineMessage, service_name: str) -> TimestampRecord:
        """Mark when a service starts processing."""
        ts = message.add_timestamp(service_name)
        if not ts.received_time:
            ts.received_time = time.time()
        ts.start_time = time.time()
        return ts
    
    @staticmethod
    def mark_completed(message: PipelineMessage, service_name: str) -> TimestampRecord:
        """Mark when a service completes processing."""
        ts = message.add_timestamp(service_name)
        ts.end_time = time.time()
        return ts
    
    @staticmethod
    def display_service_timestamp(ts: TimestampRecord, indent: int = 0):
        """Display timestamp information for a single service."""
        indent_str = "  " * indent
        
        if not ts.start_time:
            return
            
        start_str = datetime.fromtimestamp(ts.start_time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if ts.received_time:
            received_str = datetime.fromtimestamp(ts.received_time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"{indent_str}[{ts.service_name}]")
            print(f"{indent_str}  Received: {received_str}")
            print(f"{indent_str}  Started: {start_str}")
        else:
            print(f"{indent_str}[{ts.service_name}]")
            print(f"{indent_str}  Started: {start_str}")
            
        if ts.end_time:
            end_str = datetime.fromtimestamp(ts.end_time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            duration_ms = (ts.end_time - ts.start_time) * 1000
            print(f"{indent_str}  Completed: {end_str}")
            print(f"{indent_str}  Duration: {duration_ms:.2f}ms")
        else:
            print(f"{indent_str}  Status: Processing...")
    
    @staticmethod
    def display_pipeline_execution(message: PipelineMessage):
        """Display complete pipeline execution timeline."""
        print("\n" + "="*60)
        print("=== Pipeline Execution Timeline ===")
        print("="*60)
        
        # Display services in order of execution
        service_order = [
            "service_a_story_generator",
            "service_b_story_analyzer",
            "service_c_parallel_hub",
            "service_d_aggregator"
        ]
        
        for service_name in service_order:
            ts = message.get_timestamp(service_name)
            if ts:
                service_display_name = {
                    "service_a_story_generator": "Service A: Story Generator",
                    "service_b_story_analyzer": "Service B: Story Analyzer",
                    "service_c_parallel_hub": "Service C: Parallel Processing Hub",
                    "service_d_aggregator": "Service D: Final Aggregator"
                }.get(service_name, service_name)
                
                print(f"\n[{service_display_name}]")
                TimestampTracker.display_service_timestamp(ts, indent=1)
                
                # Display parallel services if we're at the parallel hub
                if service_name == "service_c_parallel_hub":
                    parallel_services = [
                        ("service_c1_image_concept", "Service C1: Image Concept"),
                        ("service_c2_audio_script", "Service C2: Audio Script"),
                        ("service_c3_translation", "Service C3: Translation"),
                        ("service_c4_formatting", "Service C4: Formatting")
                    ]
                    
                    parallel_timestamps = []
                    for ps_name, ps_display in parallel_services:
                        ps_ts = message.get_timestamp(ps_name)
                        if ps_ts and ps_ts.start_time:
                            parallel_timestamps.append((ps_ts, ps_display))
                    
                    if parallel_timestamps:
                        print("\n  [Parallel Services]")
                        for ps_ts, ps_display in parallel_timestamps:
                            start_str = datetime.fromtimestamp(ps_ts.start_time).strftime("%H:%M:%S.%f")[:-3]
                            if ps_ts.end_time:
                                end_str = datetime.fromtimestamp(ps_ts.end_time).strftime("%H:%M:%S.%f")[:-3]
                                duration_ms = (ps_ts.end_time - ps_ts.start_time) * 1000
                                print(f"    [{ps_display}] Started: {start_str}, Completed: {end_str} ({duration_ms:.2f}ms)")
                            else:
                                print(f"    [{ps_display}] Started: {start_str}, Status: Processing...")
                        
                        # Show parallel batch completion
                        if all(ps_ts.end_time for ps_ts, _ in parallel_timestamps):
                            max_end = max(ps_ts.end_time for ps_ts, _ in parallel_timestamps)
                            max_end_str = datetime.fromtimestamp(max_end).strftime("%H:%M:%S.%f")[:-3]
                            min_start = min(ps_ts.start_time for ps_ts, _ in parallel_timestamps)
                            max_duration = (max_end - min_start) * 1000
                            print(f"\n    Parallel Batch Completed: {max_end_str} (max duration: {max_duration:.2f}ms)")
        
        # Display total duration
        if message.timestamps:
            all_end_times = [ts.end_time for ts in message.timestamps.values() if ts.end_time]
            all_start_times = [ts.start_time for ts in message.timestamps.values() if ts.start_time]
            if all_start_times and all_end_times:
                total_start = min(all_start_times)
                total_end = max(all_end_times)
                total_duration_ms = (total_end - total_start) * 1000
                print(f"\n{'='*60}")
                print(f"Total Pipeline Duration: {total_duration_ms:.2f}ms")
                print("="*60 + "\n")

