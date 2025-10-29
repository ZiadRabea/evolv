from django.urls import path
from.views import *
urlpatterns = [
    path('sign_up/', sign_up, name="signup"),
]