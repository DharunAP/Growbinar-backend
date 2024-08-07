from django.urls import path
from .views import *                                    # importing views to be called for each route
from core import routes             # importing url routes from the core files in the project dir


urlpatterns = [
    path(routes.MENTEE_SIGNUP_ROUTE, MenteeSignup,name='mentee-signup'),
    path(routes.MENTOR_SIGNUP_ROUTE, MentorSignup,name='mentor-signup'),
    path(routes.VERIFY_MENTEE_ROUTE, VerifyMentee,name='verify-mentee-email'),
    path(routes.VERIFY_MENTOR_ROUTE, VerifyMentor,name='verify-mentor-email'),
    path(routes.MENTOR_DETAILS,getMentorDetails,name="get-mentor-details"),
    path(routes.MENTEE_DETAILS,getMenteeDetails,name="get-mentee-details"),
    path(routes.LOGIN_ROUTE,user_login,name="login-route"),
    path(routes.RESEND_MAIL,resendMail,name = 'resend-mail'),
    path(routes.HOME_COUNT, home_page_count, name='home-page-count'),
    path(routes.CommonEndpoint,checkUserDetails, name="common-endpoint"),
    path(routes.userLogout,user_logout,name='logout'),
    path(routes.SAMPLE_TEMPLATE_EMAIL,verifyMailSampleTemplate)
]