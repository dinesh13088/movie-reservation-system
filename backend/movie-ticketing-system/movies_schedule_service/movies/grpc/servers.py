import os
import sys
from concurrent import futures

import grpc

# Make the generated protobuf stubs importable.
_GEN_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "protos", "generated")
)
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

import screening_pb2  # noqa: E402
import screening_pb2_grpc  # noqa: E402

from movies.models import Screening  # noqa: E402


class ScreeningServiceServicer(screening_pb2_grpc.ScreeningServiceServicer):
    """gRPC service exposing read-only screening data to other microservices.

    Used by the Reservations service to validate a screening before holding seats.
    """

    def _screening_to_proto(self, screening):
        return screening_pb2.Screening(
            id=str(screening.id),
            movie_id=str(screening.movie_id),
            title=screening.movie.title,
            theater_id=str(screening.theater_id),
            hall_id=str(screening.hall_id),
            theater_name=screening.theater_name,
            hall_name=screening.hall_name,
            start_datetime=screening.start_datetime.isoformat(),
            end_datetime=screening.end_datetime.isoformat(),
            status=screening.status,
        )

    def GetScreening(self, request, context):
        try:
            screening = Screening.objects.select_related("movie").get(id=request.screening_id)
        except Screening.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Screening not found.")
            return screening_pb2.Screening()
        return self._screening_to_proto(screening)

    def ValidateScreening(self, request, context):
        try:
            screening = Screening.objects.select_related("movie").get(id=request.screening_id)
        except Screening.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Screening not found.")
            return screening_pb2.ValidateScreeningResponse(valid=False, reason="Screening not found.")

        if screening.status != Screening.STATUS_SCHEDULED:
            return screening_pb2.ValidateScreeningResponse(
                valid=False,
                screening_id=str(screening.id),
                movie_id=str(screening.movie_id),
                theater_id=str(screening.theater_id),
                hall_id=str(screening.hall_id),
                start_datetime=screening.start_datetime.isoformat(),
                reason=f"Screening status is {screening.status}.",
            )

        return screening_pb2.ValidateScreeningResponse(
            valid=True,
            screening_id=str(screening.id),
            movie_id=str(screening.movie_id),
            theater_id=str(screening.theater_id),
            hall_id=str(screening.hall_id),
            start_datetime=screening.start_datetime.isoformat(),
            reason="",
        )

    def ListScreeningsByMovie(self, request, context):
        qs = Screening.objects.filter(movie_id=request.movie_id, status="Scheduled").order_by("start_datetime")
        for screening in qs:
            yield self._screening_to_proto(screening)
