

MENTOR_SIGNUP_ROUTE = "mentorSignup/"
MENTEE_SIGNUP_ROUTE = "menteeSignup/"
LOGIN_ROUTE = "login/"
VERIFY_MENTOR_ROUTE = 'mentor/verifyEmail/'
VERIFY_MENTEE_ROUTE = 'mentee/verifyEmail/'
MENTOR_DETAILS = 'mentorDetails/'
MENTEE_DETAILS = 'menteeDetails/'
LIST_MENTORS = 'listMentors/'
MENTOR_PROFILE = 'mentors/'
MENTEE_PROFILE = 'mentees/'
CREATE_AVAILABLE_SESSIONS = 'availableSessions/'
BOOK_SESSION = 'bookSession/'
SESSION_CREATION = 'sessionFeedback/'
RESEND_MAIL = 'resendMail/'
CommonEndpoint = 'commonEndpoint/'

userLogin = 'login/'

upcomingSesions = 'upcoming-sessions/'

mentorDetails = 'mentor-details/'

userLogout = 'logout/'

newsession = 'new-sessions/<str:mentee_id>'

availablesession = 'available-sessions/'

cancelsession = 'cancel-sessions/'

listMentee = 'Mentee-listing/'

Query = 'Query/'

# '/mentors/234'  get method -> return details of the mentor 234
# '/mentors/' get method return -> all mentors
# '/listMentors/' {'id':23} get fetch all the menors who mentored mentee 23 
userLogin = 'login/'