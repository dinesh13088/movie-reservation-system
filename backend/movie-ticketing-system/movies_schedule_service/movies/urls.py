from django.urls import path
from django.http import HttpResponse
from .views import MovieDetails, MovieScrapeTrigger, MovieScrapeStatus


def home(request):
    return HttpResponse("hello")


urlpatterns = [
    path('', home, name='home'),
    path('movies/', MovieDetails.as_view(), name='movie-details'),
    path('movies/scrape/', MovieScrapeTrigger.as_view(), name='movie-scrape-trigger'),
    path('movies/scrape/status/<str:task_id>/', MovieScrapeStatus.as_view(), name='movie-scrape-status'),
]
