from django.urls import path
from .views import *           # importing views to be called for each route
from static import routes      # importing url routes from the static files in the project dir

urlpatterns = [
    path(routes.CREATE_AVAILABLE_SESSIONS, createAvailableSession, name='create-available-sessions'),
    path(routes.BOOK_SESSION,bookSession,name='book-session'),
    path(routes.SESSION_CREATION,sessionFeedback,name='session-feedback'),
    
    path(routes.UPCOMMING_SESSION_MENTEE,upcoming_sessions_mentee,name='upcomming-session-mentee'),
    path(routes.upcomingSesions,upcoming_sessions,name='upcomming-sessions'),
    path(routes.newsession, new_sessions_booking, name = 'new-session-bboking'),
    path(routes.cancelsession, session_cancellation, name = 'cancel-session')

]