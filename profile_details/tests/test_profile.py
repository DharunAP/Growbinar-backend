from django.test import TestCase,Client
from django.urls import reverse
from static.models import Mentee,Mentor,AuthToken,AvailabeSession
import json

        # client = used to create the HTTP against the django app

class mentor_details_testing(TestCase) :
    def test_mentor_details(self) :
        client = Client()
        
        val = Mentor.objects.create(
            first_name="John",
            last_name="Doe",
            country="USA",
            email_id="john.doe@example.com",
            is_email_verified=True,
            phone_number="+1234567890",
            password="hashed_password",
            gender="Male",
            date_of_birth="1990-01-01",
            city="New York",
            bio="Experienced software developer with a passion for mentoring.",
            profile_picture_url="http://example.com/profiles/johndoe.jpg",
            areas_of_expertise=["Python", "Django", "Machine Learning"],
            number_of_likes=150,
            languages=["English", "Spanish"],
            mentor_experience=5.0,
            designation="Senior Developer",
            company="Tech Solutions Inc.",
            count_of_sessions=25
        )
        val.save()

        mentor_id = val.id
        # self.assertEquals(mentor_id,1)

        ses = AvailabeSession.objects.create(
            id = mentor_id,
            availableSlots = [
                {"date":"2024-06-13","from":"23:39:00","to":"00:00:00"}
            ]
        )

        ses.save()
        self.assertEquals(ses.id,8)

# lets start here

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from static.models import Mentor, Mentee, Experience, AvailabeSession, RequestedSession, BookedSession, Session, Testimonial
from django.utils import timezone
from Authentication.jwtVerification import create_jwt_token  # Assuming you have a function to create JWT tokens


# class ViewsTests(APITestCase):

#     def setUp(self):
#         self.mentor = Mentor.objects.create(
#             first_name='John', 
#             last_name='Doe', 
#             designation='Engineer', 
#             company='TechCorp', 
#             languages='English', 
#             bio='Experienced Engineer', 
#             is_email_verified=True, 
#             city='New York',
#             mentor_experience=5
#         )
#         self.mentee = Mentee.objects.create(
#             first_name='Jane', 
#             last_name='Doe', 
#             role='Student', 
#             organization='University', 
#             languages='English', 
#             description='Interested in Tech', 
#             city='Boston'
#         )
#         self.experience = Experience.objects.create(
#             referenced_id=self.mentee.id, 
#             company='TechCorp', 
#             from_duration=timezone.now(), 
#             to_duration=timezone.now(), 
#             role_type='mentee', 
#             role='Intern', 
#             description='Worked on projects'
#         )
#         self.session = Session.objects.create(
#             mentor=self.mentor,
#             start_time=timezone.now(),
#             end_time=timezone.now(),
#             is_booked=True
#         )
#         self.booked_session = BookedSession.objects.create(
#             requested_session_id=self.session.id,
#             is_completed=True
#         )
#         self.testimonial = Testimonial.objects.create(
#             mentor=self.mentor, 
#             mentee=self.mentee, 
#             content='Great mentor!'
#         )
#         self.available_session = AvailabeSession.objects.create(
#             mentor=self.mentor,
#             availableSlots=[{'date': '2024-07-01', 'from': '10:00:00', 'to': '11:00:00'}]
#         )
#         self.valid_token = create_jwt_token(self.mentee)  # Assuming this function generates a valid token for a mentee
#         self.valid_token_mentor = create_jwt_token(self.mentor)  # Assuming this function generates a valid token for a mentor
#         self.invalid_token = "invalidtoken"


class list_all_mentors_and_mentees(TestCase) :
    def test_list_all_mentors(self) :
        client = Client()
        print("no pain no gain")

        response = client.get(reverse('list-mentors'))
        print(response.content, 'this is the response of the test 😑')
        json_response = response.json()
        self.assertEqual(response.status_code,200)
        





# response = client.post(reverse('login-route'), data=data)
        #     print(response.content)

        #     # You can also parse the JSON content if applicable
        #     json_response = response.json()
        #     print(json_response)
        #     print(response,' -- ')
        #     self.assertEquals(response.content, 'jj')        

