

MENTOR_SIGNUP_ROUTE = "mentorSignup/"
MENTEE_SIGNUP_ROUTE = "menteeSignup/"
LOGIN_ROUTE = "login/"
VERIFY_MENTOR_ROUTE = 'mentor/verifyEmail/'
VERIFY_MENTEE_ROUTE = 'mentee/verifyEmail/'
MENTOR_DETAILS = 'mentorDetails/'
MENTEE_DETAILS = 'menteeDetails/'
LIST_MENTORS = 'listMentors/'
MENTOR_PROFILE = 'mentors/'
MENTEE_PROFILE = 'mentees/<str:id>/'
CREATE_AVAILABLE_SESSIONS = 'availableSessions/'

# '/mentors/234'  get method -> return details of the mentor 234
# '/mentors/' get method return -> all mentors
# '/listMentors/' {'id':23} get fetch all the menors who mentored mentee 23 
userLogin = 'login/'