# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from .authentication import KeyCloakAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import MovieDetail, ScrapeTask
from .serializers import MovieDetailSerializer, ScrapeTaskSerializer
from .tasks import scrape_movies


class MovieDetails(APIView):
    authentication_classes = [KeyCloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            movies = MovieDetail.objects.all().order_by("-created_at")
            serializer = MovieDetailSerializer(movies, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"API Error: {e}")
            return Response({
                "error": "Failed to fetch movie details",
                "debug_message": str(e)
            }, status=500)


class MovieScrapeTrigger(APIView):
    """Trigger an asynchronous movie-scraping Celery task."""

    authentication_classes = [KeyCloakAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            scrape_task = ScrapeTask.objects.create(
                status=ScrapeTask.STATUS_PENDING,
            )
            task = scrape_movies.delay(scrape_task_id=str(scrape_task.id))
            scrape_task.celery_task_id = task.id
            scrape_task.save(update_fields=["celery_task_id", "updated_at"])

            return Response({
                "message": "Movie scraping has been scheduled successfully.",
                "task_id": task.id,
                "status": "PENDING",
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(f"Scrape trigger error: {e}")
            return Response({
                "error": "Failed to schedule movie scraping",
                "debug_message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieScrapeStatus(APIView):
    """Check the status of a scraping task by Celery task ID."""

    authentication_classes = [KeyCloakAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            scrape_task = ScrapeTask.objects.get(celery_task_id=task_id)
            serializer = ScrapeTaskSerializer(scrape_task)
            return Response(serializer.data)
        except ScrapeTask.DoesNotExist:
            return Response({
                "error": "Task not found",
                "task_id": task_id,
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Scrape status error: {e}")
            return Response({
                "error": "Failed to fetch task status",
                "debug_message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
