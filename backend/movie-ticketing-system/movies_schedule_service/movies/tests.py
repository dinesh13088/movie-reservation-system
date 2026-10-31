from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from celery import current_app

from movies.models import MovieDetail, ScrapeTask
from movies.tasks import scrape_movies


class CeleryAppTests(TestCase):
    """Tests for Celery application initialization and task discovery."""

    def test_celery_app_configured(self):
        self.assertIsNotNone(current_app)
        self.assertEqual(current_app.main, "movie_services")

    def test_scrape_movies_task_registered(self):
        registered = current_app.tasks.get("movies.tasks.scrape_movies")
        self.assertIsNotNone(registered, "scrape_movies task not registered with Celery")


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CELERY_BROKER_URL="redis://localhost:6379/0",
    CELERY_RESULT_BACKEND="redis://localhost:6379/1",
)
class ScrapeMovieTaskTests(TestCase):
    """Tests for the scrape_movies Celery task."""

    SCRAPED_MOVIES = [
        {
            "Title": "Test Movie One",
            "Image_URL": "https://example.com/poster1.jpg",
            "Rating": "PG-13",
            "Language": "English",
            "Genres": ["Action", "Drama"],
            "Genre_language": "English | Action, Drama",
        },
        {
            "Title": "Test Movie Two",
            "Image_URL": "https://example.com/poster2.jpg",
            "Rating": "R",
            "Language": "Hindi",
            "Genres": ["Romance"],
            "Genre_language": "Hindi | Romance",
        },
    ]

    @patch("movies.scraper.scrape_movies.scrape_movies")
    def test_successful_scrape_creates_records(self, mock_scrape):
        mock_scrape.return_value = self.SCRAPED_MOVIES

        result = scrape_movies.apply()

        self.assertEqual(result.status, "SUCCESS")
        summary = result.result
        self.assertEqual(summary["movies_fetched"], 2)
        self.assertEqual(summary["movies_created"], 2)
        self.assertEqual(summary["movies_updated"], 0)
        self.assertEqual(summary["movies_failed"], 0)

        self.assertEqual(MovieDetail.objects.count(), 2)
        self.assertTrue(MovieDetail.objects.filter(title="Test Movie One").exists())
        self.assertTrue(MovieDetail.objects.filter(title="Test Movie Two").exists())

    @patch("movies.scraper.scrape_movies.scrape_movies")
    def test_duplicate_movies_are_updated_not_duplicated(self, mock_scrape):
        mock_scrape.return_value = self.SCRAPED_MOVIES

        # First run: create
        scrape_movies.apply()
        self.assertEqual(MovieDetail.objects.count(), 2)

        # Second run with modified data: update
        modified = list(self.SCRAPED_MOVIES)
        modified[0]["Rating"] = "R"
        mock_scrape.return_value = modified
        scrape_movies.apply()

        self.assertEqual(MovieDetail.objects.count(), 2)
        movie = MovieDetail.objects.get(title="Test Movie One")
        self.assertEqual(movie.rating, "R")

    @patch("movies.scraper.scrape_movies.scrape_movies")
    def test_scrape_source_failure_triggers_retry(self, mock_scrape):
        mock_scrape.side_effect = Exception("QFX site unreachable")

        with self.assertRaises(Exception):
            scrape_movies.apply()

    @patch("movies.scraper.scrape_movies.scrape_movies")
    def test_per_movie_failure_is_isolated(self, mock_scrape):
        mock_scrape.return_value = [
            {
                "Title": "Good Movie",
                "Image_URL": "",
                "Rating": "PG",
                "Language": "English",
                "Genres": [],
                "Genre_language": "English",
            },
            {
                "Title": "Bad Movie",
                "Image_URL": "",
                "Rating": "",
                "Language": "",
                "Genres": [],
                "Genre_language": "",
            },
        ]

        mock_obj = MagicMock()
        with patch(
            "movies.models.MovieDetail.objects.update_or_create",
            side_effect=[(mock_obj, True), Exception("DB error")],
        ):
            result = scrape_movies.apply()

        summary = result.result
        self.assertEqual(summary["movies_fetched"], 2)
        self.assertEqual(summary["movies_created"], 1)
        self.assertEqual(summary["movies_failed"], 1)


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class ScrapeAPIEndpointTests(TestCase):
    """Tests for the scrape trigger and status API endpoints."""

    def setUp(self):
        self.client = APIClient()
        # Force authenticate as a dummy user so KeyCloakAuthentication passes
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    @patch("movies.tasks.scrape_movies.delay")
    def test_scrape_trigger_returns_task_id(self, mock_delay):
        mock_delay.return_value.id = "test-task-id-123"

        url = reverse("movie-scrape-trigger")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["message"], "Movie scraping has been scheduled successfully.")
        self.assertEqual(response.data["task_id"], "test-task-id-123")
        self.assertEqual(response.data["status"], "PENDING")
        mock_delay.assert_called_once()

    def test_scrape_status_not_found(self):
        url = reverse("movie-scrape-status", kwargs={"task_id": "nonexistent-task-id"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("movies.tasks.scrape_movies.delay")
    def test_scrape_status_returns_task_data(self, mock_delay):
        mock_delay.return_value.id = "test-task-id-456"

        # Trigger a scrape
        trigger_url = reverse("movie-scrape-trigger")
        self.client.post(trigger_url, {}, format="json")

        scrape_task = ScrapeTask.objects.get(celery_task_id="test-task-id-456")

        # Check status
        status_url = reverse("movie-scrape-status", kwargs={"task_id": "test-task-id-456"})
        response = self.client.get(status_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["celery_task_id"], "test-task-id-456")
        self.assertEqual(response.data["status"], ScrapeTask.STATUS_PENDING)
