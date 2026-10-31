"""Management command to run the Movies service gRPC server."""

import os
import sys
import signal
from concurrent import futures

import grpc
from django.core.management.base import BaseCommand
from django.conf import settings

_GEN_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "protos", "generated")
)
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

import screening_pb2_grpc  # noqa: E402
from movies.grpc.servers import ScreeningServiceServicer  # noqa: E402

GRPC_PORT = os.getenv("MOVIES_GRPC_PORT", "50051")


class Command(BaseCommand):
    help = "Run the Movies service gRPC server."

    def handle(self, *args, **options):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        screening_pb2_grpc.add_ScreeningServiceServicer_to_server(
            ScreeningServiceServicer(), server
        )
        listen_addr = f"[::]:{GRPC_PORT}"
        server.add_insecure_port(listen_addr)
        server.start()
        self.stdout.write(self.style.SUCCESS(f"Movies gRPC server listening on {listen_addr}"))

        def stop(signum, frame):
            self.stdout.stdout and self.stdout.write("Shutting down gRPC server...")
            server.stop(grace=5)
            sys.exit(0)

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)

        server.wait_for_termination()
