from django.urls import path
from .views import *           # importing views to be called for each route
from static import routes      # importing url routes from the static files in the project dir

urlpatterns = [
    path(routes.LIST_MENTORS, listAllMentors, name='list-mentors'),
    path(routes.MENTEE_PROFILE, menteeDetails, name="mentee-details"),
    path(routes.MENTOR_PROFILE, listMentorsOfMentee, name='list-mentors-of-mentee'),
]