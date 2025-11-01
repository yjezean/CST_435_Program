"""
Core pipeline implementation for local execution mode.
This module provides the pipeline coordination logic.
"""
from typing import Callable
from core.message import PipelineMessage
from core.timestamp_tracker import TimestampTracker


class Pipeline:
    """Pipeline coordinator for local execution."""
    
    def __init__(self):
        self.services = {}
        self.tracker = TimestampTracker()
    
    def register_service(self, name: str, service_func: Callable):
        """Register a service function."""
        self.services[name] = service_func
    
    def execute_pipeline(self, message: PipelineMessage, service_chain: list) -> PipelineMessage:
        """
        Execute services in the specified chain.
        
        Args:
            message: Initial pipeline message
            service_chain: List of service names to execute in order
            
        Returns:
            Final message after pipeline execution
        """
        for service_name in service_chain:
            if service_name in self.services:
                # Mark received
                self.tracker.mark_received(message, service_name)
                
                # Mark started
                self.tracker.mark_started(message, service_name)
                
                # Execute service
                service_func = self.services[service_name]
                message = service_func(message)
                
                # Mark completed
                self.tracker.mark_completed(message, service_name)
            else:
                raise ValueError(f"Service {service_name} not registered")
        
        return message

