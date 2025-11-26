"""
Message format for pipeline communication with timestamp tracking.
"""
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class TimestampRecord:
    """Record of timestamps for a service invocation."""
    service_name: str
    received_time: Optional[float] = None  # Unix timestamp when request received
    start_time: Optional[float] = None     # Unix timestamp when processing started
    end_time: Optional[float] = None       # Unix timestamp when processing completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with formatted timestamps."""
        result = {
            "service_name": self.service_name,
        }
        
        if self.received_time:
            result["received"] = datetime.fromtimestamp(self.received_time).isoformat()
            result["received_timestamp"] = self.received_time
        
        if self.start_time:
            result["started"] = datetime.fromtimestamp(self.start_time).isoformat()
            result["started_timestamp"] = self.start_time
            
        if self.end_time:
            result["completed"] = datetime.fromtimestamp(self.end_time).isoformat()
            result["completed_timestamp"] = self.end_time
            
        if self.start_time and self.end_time:
            duration_ms = (self.end_time - self.start_time) * 1000
            result["duration_ms"] = round(duration_ms, 2)
            
        return result


@dataclass
class PipelineMessage:
    """Message passed between services in the pipeline."""
    # Core data
    user_input: str  # Original user prompt
    story_text: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    
    # Parallel service results
    image_concept: Optional[Dict[str, Any]] = None
    audio_script: Optional[Dict[str, Any]] = None
    translations: Optional[Dict[str, str]] = None
    formatted_output: Optional[Dict[str, str]] = None
    
    # Timestamp tracking
    timestamps: Dict[str, TimestampRecord] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_timestamp(self, service_name: str) -> TimestampRecord:
        """Create and add a new timestamp record for a service."""
        if service_name not in self.timestamps:
            self.timestamps[service_name] = TimestampRecord(service_name=service_name)
        return self.timestamps[service_name]
    
    def get_timestamp(self, service_name: str) -> Optional[TimestampRecord]:
        """Get timestamp record for a service."""
        return self.timestamps.get(service_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        result = {
            "user_input": self.user_input,
            "timestamps": {
                name: ts.to_dict() for name, ts in self.timestamps.items()
            }
        }
        
        if self.story_text:
            result["story"] = {
                "text": self.story_text,
                "word_count": len(self.story_text.split()) if self.story_text else 0,
            }
            
        if self.analysis:
            result["analysis"] = self.analysis
            
        if self.image_concept:
            result["image_concept"] = self.image_concept
            
        if self.audio_script:
            result["audio_script"] = self.audio_script
            
        if self.translations:
            result["translations"] = self.translations
            
        if self.formatted_output:
            result["formatted_output"] = self.formatted_output
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        # Calculate total duration
        if self.timestamps:
            all_end_times = [ts.end_time for ts in self.timestamps.values() if ts.end_time]
            all_start_times = [ts.start_time for ts in self.timestamps.values() if ts.start_time]
            if all_start_times and all_end_times:
                total_start = min(all_start_times)
                total_end = max(all_end_times)
                result["total_duration_ms"] = round((total_end - total_start) * 1000, 2)
                
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineMessage":
        """Reconstruct a PipelineMessage from a dict (the inverse of to_dict).

        This will preserve timestamps and nested fields where available.
        """
        pm = cls(user_input=data.get("user_input", ""))
        pm.story_text = data.get("story_text") or data.get("story") and data.get("story").get("text")
        pm.analysis = data.get("analysis")
        pm.image_concept = data.get("image_concept")
        pm.audio_script = data.get("audio_script")
        pm.translations = data.get("translations")
        pm.formatted_output = data.get("formatted_output")
        pm.metadata = data.get("metadata", {}) or {}

        # Reconstruct timestamps if present
        ts_data = data.get("timestamps") or {}
        for name, tdict in ts_data.items():
            try:
                received = tdict.get("received_timestamp")
                started = tdict.get("started_timestamp")
                completed = tdict.get("completed_timestamp")
                tr = TimestampRecord(service_name=name,
                                     received_time=received,
                                     start_time=started,
                                     end_time=completed)
                pm.timestamps[name] = tr
            except Exception:
                # Ignore malformed timestamp entries
                continue

        return pm

