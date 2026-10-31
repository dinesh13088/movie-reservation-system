import uuid
from django.db import models
from django.utils import timezone


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "genres"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=100, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    rating = models.CharField(max_length=20, blank=True)
    poster_url = models.URLField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)

    class Meta:
        db_table = "movies"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ScreeningSchedule(models.Model):
    """Recurring schedule that generates Screening instances for specific dates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="schedules"
    )
    # References owned by the Theaters service (separate database).
    theater_id = models.UUIDField()
    hall_id = models.UUIDField()
    theater_name = models.CharField(max_length=200)
    hall_name = models.CharField(max_length=100)
    start_time = models.TimeField()  # e.g. 19:00
    day_of_week = models.SmallIntegerField(  # 0=Monday ... 6=Sunday
        default=0,
        help_text="Day of week for weekly recurrence (0=Monday, 6=Sunday).",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "screening_schedules"
        ordering = ["start_date", "start_time"]

    def __str__(self):
        return f"{self.movie.title} @ {self.theater_name}/{self.hall_name}"


class Screening(models.Model):
    """A concrete screening instance (one showtime in a hall)."""

    STATUS_SCHEDULED = "Scheduled"
    STATUS_COMPLETED = "Completed"
    STATUS_CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(
        ScreeningSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="screenings",
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="screenings"
    )
    theater_id = models.UUIDField()
    hall_id = models.UUIDField()
    theater_name = models.CharField(max_length=200)
    hall_name = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screenings"
        ordering = ["start_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["theater_id", "hall_id", "start_datetime"],
                name="unique_hall_screening_at_time",
            ),
        ]

    def __str__(self):
        return f"{self.movie.title} - {self.start_datetime} ({self.hall_name})"

    @property
    def is_scheduled(self):
        return self.status == self.STATUS_SCHEDULED


class MovieDetail(models.Model):
    """Snapshot of scraped movie information, refreshed by the background job."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    image_url = models.URLField(blank=True)
    rating = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=100, blank=True)
    genres = models.JSONField(default=list, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "movie_details"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ScrapeTask(models.Model):
    """Persistent record of a movie-scraping task invocation."""

    STATUS_PENDING = "PENDING"
    STATUS_STARTED = "STARTED"
    STATUS_RETRY = "RETRY"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILURE = "FAILURE"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_STARTED, "Started"),
        (STATUS_RETRY, "Retry"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILURE, "Failure"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    celery_task_id = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    movies_fetched = models.PositiveIntegerField(default=0)
    movies_created = models.PositiveIntegerField(default=0)
    movies_updated = models.PositiveIntegerField(default=0)
    movies_failed = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scrape_tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"ScrapeTask {self.celery_task_id} ({self.status})"
