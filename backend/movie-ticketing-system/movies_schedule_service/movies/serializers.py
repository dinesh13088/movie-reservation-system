from rest_framework import serializers
from .models import Genre, Movie, MovieDetail, ScreeningSchedule, Screening, ScrapeTask


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "created_at"]


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "language",
            "duration_minutes",
            "rating",
            "poster_url",
            "release_date",
            "is_active",
            "genres",
            "created_at",
            "updated_at",
        ]


class MovieListSerializer(serializers.ModelSerializer):
    """Flattened output matching the frontend's expected movie shape."""

    Title = serializers.CharField(source="title")
    Image_URL = serializers.CharField(source="poster_url")
    Rating = serializers.CharField(source="rating")
    Language = serializers.CharField(source="language")
    Genres = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = Movie
        fields = ["id", "Title", "Image_URL", "Rating", "Language", "Genres"]


class ScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screening
        fields = [
            "id",
            "movie",
            "theater_id",
            "hall_id",
            "theater_name",
            "hall_name",
            "start_datetime",
            "end_datetime",
            "status",
            "created_at",
        ]


class ScreeningListSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Screening
        fields = [
            "id",
            "movie",
            "movie_title",
            "theater_id",
            "hall_id",
            "theater_name",
            "hall_name",
            "start_datetime",
            "end_datetime",
            "status",
        ]


class ScreeningScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningSchedule
        fields = "__all__"


class MovieDetailSerializer(serializers.ModelSerializer):
    """Serializer for the scraped MovieDetail snapshot (read-only API)."""

    class Meta:
        model = MovieDetail
        fields = [
            "id",
            "title",
            "image_url",
            "rating",
            "language",
            "genres",
            "detail",
            "created_at",
            "updated_at",
        ]


class ScrapeTaskSerializer(serializers.ModelSerializer):
    """Serializer for persistent scrape-task tracking."""

    class Meta:
        model = ScrapeTask
        fields = [
            "id",
            "celery_task_id",
            "status",
            "movies_fetched",
            "movies_created",
            "movies_updated",
            "movies_failed",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
