from django.urls import path
from .views import *           # importing views to be called for each route
from static import routes      # importing url routes from the static files in the project dir

urlpatterns = [
    path(routes.CREATE_AVAILABLE_SESSIONS, createAvalableSession, name='create-available-sessions'),
    path('bookSession/',bookSession,name='book-session'),
    path('sessionFeedback/',sessionFeedback,name='session-feedback')
]