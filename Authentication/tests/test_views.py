from django.test import TestCase,Client
from django.urls import reverse
from static.models import Mentee,Mentor,AuthToken
import json

        # client = used to create the HTTP against the django app

class testingViewsMentor(TestCase) :
        
# MENTOR SIGNUP
        def test_mentor_sign(self) :
            client = Client()
            data = {
            "email_id": "musk@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentor-signup'), data=data)
            
            self.assertEquals(response.json(), 'hello')

# VERIFY MAIL FOR MENTOR
        def test_mentor_verify (self):
            client = Client()
            data = {
            "email_id": "laptop@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentor-signup'), data=data)
            id = response.json()['id']
            
            response2 = client.get(reverse('verify-mentor-email'),{'id':id})
            self.assertEquals(response2.content,200) 

# STEPPER FOR MENTOR
        def test_mentor_stepper (self):
            client = Client()
            data = {
            "email_id": "musk@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentor-signup'), data=data)
            token = response.json()['jwt_token']
            id = response.json()['id']
            
            response2 = client.get(reverse('verify-mentor-email'),{'id':id})

            data1 = {
            "first_name": "Harry",
            "last_name": "Potter",
            "country": "United States",
            "phone_number": "1234567890",
            "gender": "Female",
            "date_of_birth": "1990-01-01",
            "city": "Los Angeles",
            "bio": "Passionate about mentoring aspiring developers.",
            "profile_picture_url": "https://kinsta.com/blog/url-shortener-with-python/",
            "areas_of_expertise": ["Web Development", "JavaScript", "React"],
            "languages": ["English", "French"],
            "MentorExperience": 7.5,
            "designation": "Lead Frontend Developer",
            "company": "TechGuru"
            }
            headers = {
            'HTTP_AUTHORIZATION': f'Bearer {token}'
            }
            response3 = client.post(reverse('get-mentor-details'),data=data1,content_type='application/json',**headers)

            self.assertEquals(response3.status_code,200) 

class TestingViewsMentee (TestCase):
# TESTING MENTEE
        def test_mentee_sign(self) :
            client = Client()
            data = {
            "email_id": "musk@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentee-signup'), data=data)
            self.assertEquals(response.content, 'hhh')

# TESTING MAIL FOR MENTEE
        def test_mentor_verify (self):
            client = Client()
            data = {
            "email_id": "musk@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentee-signup'), data=data)
            id = response.json()['id']
            
            response2 = client.get(reverse('verify-mentee-email'),{'id':id})
            self.assertEquals(response2.status_code,200) 

# STEPPER FOR MENTEE
        def test_mentee_stepper (self):
            client = Client()
            data = {
            "email_id": "musk@gmail.com",
            "password": "root",
            }
            response = client.post(reverse('mentee-signup'), data=data)
            token = response.json()['jwt_token']
            id = response.json()['id']
            
            response2 = client.get(reverse('verify-mentee-email'),{'id':id})

            data1 = {
            "first_name": "John",
            "last_name": "Doe",
            "country": "USA",
            "phone_number": "+1234567890",
            "languages":["Tamil","English"],
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "city": "New York",
            "profile_picture_url": "https://images.unsplash.com/photo-1529665253569-6d01c0eaf7b6?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8cHJvZmlsZXxlbnwwfHwwfHx8MA%3D%3D",
            "areas_of_interest": ["Technology", "Science"],
            "description": "I am passionate about learning new technologies and exploring scientific advancements",
            "role": "Software Engineer",
            "organization": "Tech Company XYZ",
            "is_experience": True
            }
            headers = {
            'HTTP_AUTHORIZATION': f'Bearer {token}'
            }
            response3 = client.post(reverse('get-mentee-details'),data=data1,content_type='application/json',**headers)

            self.assertEquals(response3.status_code,200)

class TestingViewsLogin(TestCase) :
# LOGIN
        def test_login(self):
            client = Client()
            data = {
                "email_id": "musk@gmail.com",
                "password": "root",
                "user_role" : "mentor"
            }

            ins = Mentor.objects.create(
                  email_id = 'musk@gmail.com',
                  password = 'root',
                  first_name = 'elon',
                  is_email_verified = True
            )
            ins.save()

            response = client.post(reverse('login-route'), data=data)
            print(response.content)

            # You can also parse the JSON content if applicable
            json_response = response.json()
            print(json_response)
            print(response,' -- ')
            self.assertEquals(response.content, 'jj')