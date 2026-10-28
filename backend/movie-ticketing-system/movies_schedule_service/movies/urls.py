from django.urls import path
from django.http import HttpResponse
from .views import MovieDetails
def home(request):
    return HttpResponse("hello")
urlpatterns=[
    path('',home,name='home'),
    path('movies',MovieDetails.as_view())

]