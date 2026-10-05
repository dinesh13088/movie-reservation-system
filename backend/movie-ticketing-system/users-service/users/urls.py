from django.urls import path
from django.http import HttpResponse
def hello(request):
    return HttpResponse("hello world")
from .views import UserRegisterationView,LoginView,TokenRefreshView
urlpatterns = [
    path('',hello),
    path('user/register/',UserRegisterationView.as_view(),name='register-user'),
    path('user/auth/login/',LoginView.as_view(),name='login-user'),
    path('user/token/refresh/',TokenRefreshView.as_view(),name='refresh-token')


]