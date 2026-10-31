from django.apps import AppConfig

import os
from apscheduler.triggers.cron import CronTrigger
class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        from movies.tasks import scrape_movies
        from apscheduler.schedulers.background import BackgroundScheduler
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('RUN_MAIN') is None:
            schedular=BackgroundScheduler()
            def trigger_celery_scrape():
                scrape_movies.delay()
                print("APScheduler told Celery to run the scrape task!")

            schedular.add_job(
                trigger_celery_scrape,
                CronTrigger(hour=16,minute=52),
                id='scrap_movies_task',
                replace_existing=True
            )
            schedular.start()
        

