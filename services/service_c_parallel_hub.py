"""
Service C: Parallel Processing Hub
Coordinates parallel execution of multiple services (C1, C2, C3, C4).
"""
import time
import concurrent.futures
from typing import List
from core.message import PipelineMessage
from core.timestamp_tracker import TimestampTracker
from core.grpc_client import PipelineClient as _GrpcClient  # type: ignore
import os
from core import rpc as _rpc
import threading


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
    # If RPC_MODE is enabled, call remote services via RPC using env addresses, otherwise use local functions
    mode_val = os.environ.get("PIPELINE_MODE", "").lower()
    rpc_mode = (os.environ.get("RPC_MODE", "false").lower() == "true") or (mode_val == "rpc")
    grpc_mode = (mode_val == "grpc")
    parallel_services = []
    if rpc_mode or grpc_mode:
        # Determine addresses for remote services. Prefer explicit SERVICE_C?_ADDR, then C?_HOST/C?_PORT, then compose default names/ports.
        def _addr_for(specific_addr_env, host_env, default_host, default_port):
            addr = os.environ.get(specific_addr_env)
            if addr:
                return addr
            host = os.environ.get(host_env)
            port = os.environ.get(f"{host_env}_PORT") or os.environ.get("SERVICE_PORT")
            if host:
                return f"{host}:{port or default_port}"
            return f"{default_host}:{default_port}"

        parallel_services = [
            ("service_c1_image_concept", _addr_for("SERVICE_C1_ADDR", "C1_HOST", "service-c1", 50053)),
            ("service_c2_audio_script", _addr_for("SERVICE_C2_ADDR", "C2_HOST", "service-c2", 50054)),
            ("service_c3_translation", _addr_for("SERVICE_C3_ADDR", "C3_HOST", "service-c3", 50055)),
            ("service_c4_formatting", _addr_for("SERVICE_C4_ADDR", "C4_HOST", "service-c4", 50056)),
        ]
    else:
        from services.service_c1_image_concept import process_service_c1
        from services.service_c2_audio_script import process_service_c2
        from services.service_c3_translation import process_service_c3
        from services.service_c4_formatting import process_service_c4
        
        parallel_services = [
            ("service_c1_image_concept", process_service_c1),
            ("service_c2_audio_script", process_service_c2),
            ("service_c3_translation", process_service_c3),
            ("service_c4_formatting", process_service_c4),
        ]
    
    # Execute all services in parallel
    def execute_with_tracking(service_name, service_target, msg):
        """Execute a service (local or remote) with timestamp tracking.

        service_target is either a callable (local) or an address string 'host:port' for RPC.
        """
        tracker.mark_received(msg, service_name)
        tracker.mark_started(msg, service_name)
        result_msg = None
        if (rpc_mode or grpc_mode) and isinstance(service_target, str):
            host, sep, port = service_target.partition(":")
            port = int(port) if port else 8000
            try:
                if grpc_mode:
                    client = _GrpcClient(host, port)
                    result_msg = client.process(msg)
                else:
                    resp = _rpc.rpc_call(host, port, msg.to_dict())
                    result_msg = PipelineMessage.from_dict(resp)
            except Exception as e:
                mode = "gRPC" if grpc_mode else "RPC"
                print(f"{mode} call to {service_name} at {service_target} failed: {e}")
                result_msg = msg
        else:
            # Local callable
            result_msg = service_target(msg)

        tracker.mark_completed(result_msg, service_name)
        return service_name, result_msg
    
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


def _rpc_handler(params: dict) -> dict:
    pm = PipelineMessage.from_dict(params)
    tracker = TimestampTracker()
    tracker.mark_received(pm, "service_c_parallel_hub")
    tracker.mark_started(pm, "service_c_parallel_hub")
    try:
        result = process_service_c(pm)
        tracker.mark_completed(result, "service_c_parallel_hub")
        return result.to_dict()
    except Exception:
        tracker.mark_completed(pm, "service_c_parallel_hub")
        raise


if __name__ == "__main__":
    import threading, os
    from core import grpc_server as _grpc_server  # type: ignore
    mode = os.environ.get("PIPELINE_MODE", "rpc").lower()
    port = int(os.environ.get("PORT", os.environ.get("RPC_PORT", os.environ.get("SERVICE_PORT", "50057"))))
    host = os.environ.get("HOST", "0.0.0.0")
    if mode == "grpc":
        print(f"Starting gRPC server for service_c (parallel hub) on {host}:{port}")
        def _grpc_handler(pm: PipelineMessage) -> PipelineMessage:
            tracker = TimestampTracker()
            tracker.mark_received(pm, "service_c_parallel_hub")
            tracker.mark_started(pm, "service_c_parallel_hub")
            try:
                result = process_service_c(pm)
                tracker.mark_completed(result, "service_c_parallel_hub")
                return result
            except Exception:
                tracker.mark_completed(pm, "service_c_parallel_hub")
                raise
        server = _grpc_server.serve(_grpc_handler, host=host, port=port)
    else:
        print(f"Starting RPC server for service_c (parallel hub) on {host}:{port}")
        server = _rpc.serve(_rpc_handler, host=host, port=port)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down server")

