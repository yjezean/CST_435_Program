"""
Simple gRPC client wrapper to call a remote PipelineService.
"""
from typing import Optional
import grpc

from core.message import PipelineMessage
from core.grpc_utils import pipeline_message_to_proto, proto_to_pipeline_message


class PipelineClient:
    def __init__(self, host: str, port: int, options: Optional[list] = None):
        target = f"{host}:{port}"
        self._channel = grpc.insecure_channel(target, options=options or [])
        from core.grpc import pipeline_pb2_grpc

        self._stub = pipeline_pb2_grpc.PipelineServiceStub(self._channel)

    def process(self, message: PipelineMessage, timeout: Optional[float] = 10.0) -> PipelineMessage:
        req = pipeline_message_to_proto(message)
        resp = self._stub.Process(req, timeout=timeout)
        return proto_to_pipeline_message(resp)
