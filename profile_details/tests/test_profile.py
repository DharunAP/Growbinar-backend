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