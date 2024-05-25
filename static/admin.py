from django.contrib import admin
from .models import *

admin.site.register(Mentee)
admin.site.register(Mentor)
admin.site.register(Experience)
admin.site.register(Session)
admin.site.register(RequestedSession)
admin.site.register(BookedSession)
admin.site.register(SessionFeedback)
admin.site.register(AvailabeSession)
admin.site.register(AuthToken)
admin.site.register(UserQuery)
admin.site.register(Testimonial)