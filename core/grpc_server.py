"""
Common gRPC server harness for services.

Provides a server that delegates Process(request) to a provided handler function:
    handler: Callable[[PipelineMessage], PipelineMessage]
"""
from concurrent import futures
from typing import Callable
import grpc

from core.message import PipelineMessage
from core.grpc_utils import pipeline_message_to_proto, proto_to_pipeline_message


def serve(handler: Callable[[PipelineMessage], PipelineMessage], host: str = "0.0.0.0", port: int = 50051):
    from core.grpc import pipeline_pb2_grpc

    class _Servicer(pipeline_pb2_grpc.PipelineServiceServicer):
        def Process(self, request, context):
            pm = proto_to_pipeline_message(request)
            out_pm = handler(pm)
            return pipeline_message_to_proto(out_pm)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_PipelineServiceServicer_to_server(_Servicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server
