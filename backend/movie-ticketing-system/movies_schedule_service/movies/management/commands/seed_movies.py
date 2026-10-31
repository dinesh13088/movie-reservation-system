from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, date, timedelta

from movies.models import Genre, Movie, ScreeningSchedule


class Command(BaseCommand):
    help = "Seed sample movies, genres, and screening schedules for development."

    def handle(self, *args, **options):
        action, _ = Genre.objects.get_or_create(name="Action")
        scifi, _ = Genre.objects.get_or_create(name="Sci-Fi")
        drama, _ = Genre.objects.get_or_create(name="Drama")

        inception, _ = Movie.objects.get_or_create(
            title="Inception",
            defaults={
                "description": "A thief who enters the dreams of others.",
                "language": "English",
                "duration_minutes": 148,
                "rating": "PG-13",
                "poster_url": "https://image.tmdb.org/t/p/w500/inception.jpg",
                "release_date": date(2010, 7, 16),
                "is_active": True,
            },
        )
        inception.genres.set([action, scifi])

        matrix, _ = Movie.objects.get_or_create(
            title="The Matrix",
            defaults={
                "description": "A computer hacker learns reality is a simulation.",
                "language": "English",
                "duration_minutes": 136,
                "rating": "R",
                "poster_url": "https://image.tmdb.org/t/p/w500/matrix.jpg",
                "release_date": date(1999, 3, 31),
                "is_active": True,
            },
        )
        matrix.genres.set([action, scifi])

        # Placeholder UUIDs referencing theaters/halls managed by the Theaters service.
        # These should be replaced with real theater/hall ids once seeded there.
        THEATER_ID = "00000000-0000-0000-0000-000000000001"
        HALL_ID = "00000000-0000-0000-0000-000000000001"

        today = timezone.localdate()
        for movie in [inception, matrix]:
            for offset in range(3):
                show_date = today + timedelta(days=offset)
                ScreeningSchedule.objects.get_or_create(
                    movie=movie,
                    theater_id=THEATER_ID,
                    hall_id=HALL_ID,
                    start_time=time(19, 0),
                    day_of_week=show_date.weekday(),
                    start_date=show_date,
                    defaults={
                        "theater_name": "QFX City Center",
                        "hall_name": "Hall 1",
                        "end_date": show_date + timedelta(days=30),
                        "is_active": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Sample movies and schedules seeded."))
