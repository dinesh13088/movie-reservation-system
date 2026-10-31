from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "genres",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("language", models.CharField(blank=True, max_length=100)),
                ("duration_minutes", models.IntegerField(blank=True, null=True)),
                ("rating", models.CharField(blank=True, max_length=20)),
                ("poster_url", models.URLField(blank=True)),
                ("release_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "movies",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ScreeningSchedule",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("theater_id", models.UUIDField()),
                ("hall_id", models.UUIDField()),
                ("theater_name", models.CharField(max_length=200)),
                ("hall_name", models.CharField(max_length=100)),
                ("start_time", models.TimeField()),
                (
                    "day_of_week",
                    models.SmallIntegerField(
                        default=0,
                        help_text="Day of week for weekly recurrence (0=Monday, 6=Sunday).",
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="movies.movie",
                    ),
                ),
            ],
            options={
                "db_table": "screening_schedules",
                "ordering": ["start_date", "start_time"],
            },
        ),
        migrations.CreateModel(
            name="Screening",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("theater_id", models.UUIDField()),
                ("hall_id", models.UUIDField()),
                ("theater_name", models.CharField(max_length=200)),
                ("hall_name", models.CharField(max_length=100)),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Scheduled", "Scheduled"),
                            ("Completed", "Completed"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Scheduled",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="screenings",
                        to="movies.movie",
                    ),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="screenings",
                        to="movies.screeningschedule",
                    ),
                ),
            ],
            options={
                "db_table": "screenings",
                "ordering": ["start_datetime"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=["theater_id", "hall_id", "start_datetime"],
                        name="unique_hall_screening_at_time",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="movie",
            name="genres",
            field=models.ManyToManyField(
                blank=True, related_name="movies", to="movies.genre"
            ),
        ),
    ]
