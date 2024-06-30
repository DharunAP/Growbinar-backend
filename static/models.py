from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth.hashers import make_password

class Mentee(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=50,null=True,blank=True)
    email_id = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    languages = ArrayField(models.CharField(max_length=100),null=True,blank=True)
    password = models.CharField(max_length=100)
    gender = models.CharField(max_length=10,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    profile_picture_url = models.CharField(null=True,blank=True)
    areas_of_interest = ArrayField(models.CharField(max_length=100),null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    role = models.CharField(max_length=100,null=True,blank=True)
    organization = models.CharField(max_length=100,null=True,blank=True)
    is_experience = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    def __str__(self):
        return str(str(self.id)+" "+self.email_id)

class Mentor(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=50,null=True,blank=True)
    email_id = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    password = models.CharField(max_length=100)
    gender = models.CharField(max_length=10,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField(null=True,blank=True)
    profile_picture_url = models.CharField(null=True,blank=True)
    areas_of_expertise = ArrayField(models.CharField(max_length=100),null=True,blank=True)
    number_of_likes = models.IntegerField(null=True,blank=True)
    languages = ArrayField(models.CharField(max_length=100),null=True,blank=True)
    mentor_experience = models.FloatField(null=True,blank=True)
    designation = models.CharField(max_length=100,null=True,blank=True)
    company = models.CharField(max_length=100,null=True,blank=True)
    count_of_sessions = models.IntegerField(default=0)
    is_top_rated = models.BooleanField(default=False) #remove
    is_experience = models.BooleanField(default=False) #remove
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    def __str__(self):
        return str(str(self.id)+" "+self.email_id)

class AuthToken(models.Model) :
    user_type = models.CharField(max_length=100)
    referenceId = models.IntegerField()
    jwt_token = models.CharField(primary_key=True,max_length=500)
    created_date = models.DateField(auto_now_add=True)

class Experience(models.Model):
    id = models.AutoField(primary_key=True)
    from_duration = models.DateTimeField()
    to_duration = models.DateTimeField(null=True,blank=True)
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField()
    role_type = models.CharField(max_length=10, choices=[('mentor', 'Mentor'), ('mentee', 'Mentee')])
    referenced_id = models.IntegerField()
    mentorRef = models.ForeignKey(Mentor, on_delete=models.CASCADE, null=True, blank=True)
    menteeRef = models.ForeignKey(Mentee, on_delete=models.CASCADE, null=True, blank=True)

class AvailabeSession(models.Model):
    mentor = models.OneToOneField(Mentor, on_delete=models.CASCADE)
    availableSlots = ArrayField(models.JSONField(),null=True,blank=True)

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    slot_date = models.DateField()
    from_slot_time = models.TimeField()
    to_slot_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class RequestedSession(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, primary_key=True)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    reason = models.TextField()
    created_at = models.DateTimeField(null=False, auto_now_add=True)


class BookedSession(models.Model):
    id = models.AutoField(primary_key=True)
    requested_session = models.OneToOneField(RequestedSession, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    hosting_url = models.TextField()
    join_url = models.TextField()

class SessionFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    booked_session = models.OneToOneField(BookedSession, on_delete=models.CASCADE)
    description = models.TextField()
    ratings = models.IntegerField()
    created_at = models.DateTimeField(null=False, auto_now_add=True)

class UserQuery(models.Model) :
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    from_email = models.EmailField()
    to_email = models.EmailField()
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    query = models.CharField(max_length=500,null=True,blank=True)

class Testimonial(models.Model):
    id = models.AutoField(primary_key=True)
    mentor_name = models.TextField(max_length=150,default="Mentor name")
    mentor_role = models.TextField(max_length=150,default="Mentor role")
    mentor_organization = models.TextField(max_length=150,default="Mentor org")
    mentee_name = models.TextField(max_length=150,default="Mentee name")
    mentee_role = models.TextField(max_length=150,default="Mentee role")
    mentor_profile = models.TextField(max_length=150,default="Mentor profile")
    mentee_profile = models.TextField(max_length=150,default="Mentee profile")
    content = models.TextField()