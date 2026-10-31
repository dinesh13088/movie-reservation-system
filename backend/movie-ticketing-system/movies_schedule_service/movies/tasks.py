"""Celery background task for scraping movies from QFX cinemas."""

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone as tz

from .models import MovieDetail, ScrapeTask

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_movies(self, scrape_task_id=None):
    """Scrape movie listings from QFX cinemas and upsert into MovieDetail.

    The actual scraping logic lives in movies.scraper.scrape_movies (Selenium
    against https://www.qfxcinemas.com/now-showing) and is left unchanged.
    Existing movies are updated via update_or_create() instead of duplicated.

    Per-movie failures are isolated so one bad record does not abort the whole
    scrape. Returns a summary dict with created/updated/failed counts.
    """
    scrape_task = None
    if scrape_task_id:
        try:
            scrape_task = ScrapeTask.objects.get(celery_task_id=self.request.id)
            scrape_task.status = ScrapeTask.STATUS_STARTED
            scrape_task.started_at = tz.now()
            scrape_task.save(update_fields=["status", "started_at", "updated_at"])
        except ScrapeTask.DoesNotExist:
            logger.warning("ScrapeTask %s not found; continuing without tracking.", scrape_task_id)

    logger.info("Celery task %s: starting QFX movie scrape.", self.request.id)

    try:
        from .scraper.scrape_movies import scrape_movies as _scrape_movies
        movies = _scrape_movies()
    except Exception as exc:
        logger.exception("Celery task %s: QFX scraping source failed.", self.request.id)
        if scrape_task:
            scrape_task.status = ScrapeTask.STATUS_FAILURE
            scrape_task.error_message = str(exc)
            scrape_task.completed_at = tz.now()
            scrape_task.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
        raise self.retry(exc=exc)

    logger.info("Celery task %s: fetched %d movies from QFX.", self.request.id, len(movies))

    created = 0
    updated = 0
    failed = 0

    for movie in movies:
        try:
            with transaction.atomic():
                obj, was_created = MovieDetail.objects.update_or_create(
                    title=movie["Title"],
                    defaults={
                        "image_url": movie.get("Image_URL", ""),
                        "rating": movie.get("Rating", ""),
                        "language": movie.get("Language", ""),
                        "genres": movie.get("Genres", []),
                        "detail": movie.get("Genre_language", ""),
                    },
                )
                if was_created:
                    created += 1
                    logger.debug("Celery task %s: created MovieDetail '%s'.", self.request.id, movie["Title"])
                else:
                    updated += 1
                    logger.debug("Celery task %s: updated MovieDetail '%s'.", self.request.id, movie["Title"])
        except Exception as exc:
            failed += 1
            logger.exception("Celery task %s: failed to upsert movie '%s'.", self.request.id, movie.get("Title", "unknown"))

    summary = {
        "task_id": self.request.id,
        "status": "SUCCESS",
        "movies_fetched": len(movies),
        "movies_created": created,
        "movies_updated": updated,
        "movies_failed": failed,
    }

    if scrape_task:
        scrape_task.status = ScrapeTask.STATUS_SUCCESS
        scrape_task.movies_fetched = len(movies)
        scrape_task.movies_created = created
        scrape_task.movies_updated = updated
        scrape_task.movies_failed = failed
        scrape_task.completed_at = tz.now()
        scrape_task.save(update_fields=[
            "status", "movies_fetched", "movies_created", "movies_updated",
            "movies_failed", "completed_at", "updated_at",
        ])

    logger.info(
        "Celery task %s: scrape complete - fetched=%d created=%d updated=%d failed=%d.",
        self.request.id, len(movies), created, updated, failed,
    )
    return summary
