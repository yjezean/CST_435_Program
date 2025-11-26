"""
Utilities to convert between internal PipelineMessage and gRPC proto messages.

We serialize complex nested dict fields to JSON strings to keep the proto simple.
"""
import json
from typing import Dict, Any

from core.message import PipelineMessage


def _safe_dumps(obj: Any) -> str:
    if obj is None:
        return ""
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return ""


def _safe_loads(s: str):
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def pipeline_message_to_proto(pm: PipelineMessage):
    # Lazy import to avoid hard dependency when grpc mode isn't used
    from core.grpc import pipeline_pb2

    proto = pipeline_pb2.PipelineMessage(
        user_input=pm.user_input or "",
        story_text=pm.story_text or "",
        analysis_json=_safe_dumps(pm.analysis),
        image_concept_json=_safe_dumps(pm.image_concept),
        audio_script_json=_safe_dumps(pm.audio_script),
        translations_json=_safe_dumps(pm.translations),
        formatted_output_json=_safe_dumps(pm.formatted_output),
        metadata_json=_safe_dumps(pm.metadata),
        timestamps_json=_safe_dumps(
            {name: ts.to_dict() for name, ts in pm.timestamps.items()}
        ),
    )
    return proto


def proto_to_pipeline_message(proto_msg) -> PipelineMessage:
    data: Dict[str, Any] = {
        "user_input": getattr(proto_msg, "user_input", "") or "",
        "story": {"text": getattr(proto_msg, "story_text", "") or ""},
    }

    analysis = _safe_loads(getattr(proto_msg, "analysis_json", ""))
    if analysis is not None:
        data["analysis"] = analysis

    image_concept = _safe_loads(getattr(proto_msg, "image_concept_json", ""))
    if image_concept is not None:
        data["image_concept"] = image_concept

    audio_script = _safe_loads(getattr(proto_msg, "audio_script_json", ""))
    if audio_script is not None:
        data["audio_script"] = audio_script

    translations = _safe_loads(getattr(proto_msg, "translations_json", ""))
    if translations is not None:
        data["translations"] = translations

    formatted_output = _safe_loads(getattr(proto_msg, "formatted_output_json", ""))
    if formatted_output is not None:
        data["formatted_output"] = formatted_output

    metadata = _safe_loads(getattr(proto_msg, "metadata_json", ""))
    if metadata is not None:
        data["metadata"] = metadata

    timestamps = _safe_loads(getattr(proto_msg, "timestamps_json", ""))
    if timestamps is not None:
        data["timestamps"] = timestamps

    return PipelineMessage.from_dict(data)
