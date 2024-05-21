from static.models import Mentee,Mentor,Experience
from rest_framework.decorators import api_view
from static.cipher import encryptData,decryptData
from static.message_constants import LOGIN_SUCCESS,INVALID_ROLE,LOGIN_ERROR,INVALID_CREDENTIALS,STATUSES,USER_NOT_FOUND
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import MentorSerializer,MenteeSerializer,UserSerializer
from static.message_constants import STATUSES,INVALID_CREDENTIALS,USER_CREATED,EMAIL_EXISTS,SIGNUP_ERROR,VERIFIED_USER_EMAIL,ERROR_VERIFYING_USER_EMAIL,USER_DETAILS_SAVED,ERROR_SAVING_USER_DETAILS,EMAIL_NOT_VERIFIFED
from static.routes import VERIFY_MENTOR_ROUTE,VERIFY_MENTEE_ROUTE
from django.contrib.auth.hashers import make_password,check_password
from .assets import sendVerificationMail,log
from .jwtVerification import get_or_create_jwt


@api_view(['POST'])
def user_login(request):
    print("Request has Entered into User Login Page")
    log("Entered User-Login ",1)

    try:
        print(request.data)
        email = request.data.get('email')
        password = request.data.get('password')
        user_role = request.data.get('user_role')  # 'mentor' or 'mentee'
        user = None
        if user_role == 'mentor':
                 # Request entered where the user exist
            user = Mentor.objects.filter(email_id=email).first()
            log("User is Mentor",1)

        elif user_role == 'mentee':
            user = Mentee.objects.filter(email_id=email).first()
            log("User is Mentee",1)
            
        else:
            log("Invalid user_role",3)
            return JsonResponse({'message' : INVALID_ROLE},status = STATUSES['BAD_REQUEST'])
        print(user)

        if not user:
                    # Request entered were user not exist
            if user_role == 'mentor':
                log("User Not Found",2)
                return JsonResponse({'message' : USER_NOT_FOUND }, status = STATUSES['BAD_REQUEST'])
            
            else :
                log("User Not Found",2)
                return JsonResponse({'message' :USER_NOT_FOUND},status = STATUSES['BAD_REQUEST'])
            
        if check_password(password, user.password):
        # if (password == user.password):
            token = str(get_or_create_jwt(user,user_role,email))
            print(token, " tata printed ")
            log("User Logged In",1)
            return JsonResponse({
                'message': LOGIN_SUCCESS,  # Using 'message' key
                'token' : token,
                'data' : {
                    'name' : user.first_name + user.last_name,
                    'user_id' : encryptData(user.id),  # encoding the user id
                    'email' : email,
                    'role' : user_role
                }
            }, status= STATUSES['SUCCESS'])
        
        else:
            log("Invalid Credentials",3)
            
            return JsonResponse({'message' : INVALID_CREDENTIALS}, status = STATUSES['BAD_REQUEST'])
            
    except Exception as ex:
        print(ex)
        log('Error while Login  ' + str(ex),3)
        return JsonResponse({'message' : LOGIN_ERROR}, status = STATUSES['INTERNAL_SERVER_ERROR'])


@api_view(['POST'])
def MenteeSignup(request):
    log("Entered mentee-signup",1)
    try:
        # chekking weather email already exists
        if Mentee.objects.filter(email_id=request.data['email_id']).exists():
            log("Email already exists as a mentee",1)
            return Response({"message":EMAIL_EXISTS},status=STATUSES['BAD_REQUEST'])

        serializer = UserSerializer(data=request.data)
        print(request.data)
        # validating the payload
        valid=serializer.is_valid()
        if valid:
            # creating mentor object
            instance = Mentee.objects.create(email_id=request.data['email_id'],password=make_password(request.data['password']))
            instance.save()
            encryptedID = encryptData(instance.id)       # encrypting the id to send as the response
            sendVerificationMail(VERIFY_MENTEE_ROUTE+"?id="+encryptedID,request.data['email_id'])
            # log("signup successfull",1)
            log("signup successfull",1)
            return Response({'message':USER_CREATED,"id":encryptedID}, status=STATUSES['SUCCESS'])
        else:
            # sending bad request response for invalid payload
            log("invalid credentails for signup "+str(serializer.errors),2)
            print(serializer.errors)
            return Response({"message":INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log("Error creating a mentee"+str(e),3)
        return Response({'message':SIGNUP_ERROR}, status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def MentorSignup(request):
    log("Entered mentor-signup",1)
    try:
        # chekking weather email already exists
        if Mentor.objects.filter(email_id=request.data['email_id']).exists():
            log("Email already exists",2)
            return Response({"message":EMAIL_EXISTS},status=STATUSES['BAD_REQUEST'])

        serializer = UserSerializer(data=request.data)
        print(request.data)
        # validating the payload
        valid=serializer.is_valid()
        if valid:
            # creating mentor object
            instance = Mentor.objects.create(email_id=request.data['email_id'],password=make_password(request.data['password']))
            instance.save()
            log("signup successfull",1)
            encryptedID = encryptData(instance.id)      # encrypting the id to send as the response
            sendVerificationMail(VERIFY_MENTOR_ROUTE+"?id="+encryptedID,request.data['email_id'])
            return Response({'message':USER_CREATED,"id":encryptedID}, status=STATUSES['SUCCESS'])
        else:
            # sending bad request response
            log("invalid credentails for signup",2)
            print(serializer.errors)
            return Response({"message":INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log("Error creating a mentor"+str(e),3)
        return Response({'message':SIGNUP_ERROR}, status=STATUSES['INTERNAL_SERVER_ERROR'])


@api_view(['GET'])
def VerifyMentee(request):
    log('Entered email verification of mentee',1)
    try:
        # Getting mentee id from the url and setting is_email_verified to True
        menteeID = decryptData(request.GET.get('id'))
        print(menteeID)
        mentee = Mentee.objects.get(id=menteeID)
        mentee.is_email_verified = True
        mentee.save()
        log('Email verification sucess for '+menteeID,1)
        return Response({'message':VERIFIED_USER_EMAIL},status=STATUSES['SUCCESS'])
    except Exception as e:
        log("Error verifying email "+str(e),3)
        return Response({'message':ERROR_VERIFYING_USER_EMAIL},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET'])
def VerifyMentor(request):
    log('Entered email verification mentor',1)
    try:
        # Getting mentor id from the url and setting is_email_verified to True
        mentorID = decryptData(request.GET.get('id'))
        mentor = Mentor.objects.get(id=mentorID)
        mentor.is_email_verified = True
        mentor.save()
        log('Email verification sucess for '+mentorID,1)
        return Response({'message':VERIFIED_USER_EMAIL},status=STATUSES['SUCCESS'])
    except Exception as e:
        log("Error verifying email "+str(e),3)
        return Response({'message':ERROR_VERIFYING_USER_EMAIL},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def getMentorDetails(request):
    log('Entered mentor details endpoint',1)
    try:
        print(decryptData(request.data['id']))
        mentor = Mentor.objects.get(id=decryptData(request.data['id']))
        print(mentor)
        if not mentor.is_email_verified:
            log("Email not verified",2)
            return Response({'message':EMAIL_NOT_VERIFIFED},status=STATUSES['BAD_REQUEST'])
        request.data['password'] = mentor.password
        serializer = MentorSerializer(data=request.data)
        valid = serializer.is_valid()
        print(mentor)
        if valid:
            mentor.first_name=request.data['first_name']
            mentor.last_name=request.data['last_name']
            mentor.country=request.data['country']
            mentor.phone_number=request.data['phone_number']
            mentor.gender=request.data['gender']
            mentor.date_of_birth=request.data['date_of_birth']
            mentor.city=request.data['city']
            mentor.bio=request.data['bio']  
            mentor.profile_picture_url=request.data['profile_picture_url']
            mentor.areas_of_expertise=request.data['areas_of_expertise']
            mentor.number_of_likes=0
            mentor.languages=request.data['languages']
            mentor.MentorExperience=request.data['MentorExperience']
            mentor.designation=request.data['designation']
            mentor.company=request.data['company']

            mentor.save()
            log("success",1)
            return Response({'message':USER_DETAILS_SAVED},status=STATUSES['SUCCESS'])
        else:
            log('invalid details '+str(serializer.errors),2)
            return Response({'message':INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log("Error saving mentor details - "+str(e),3)
        print(e)
        return Response({'message':ERROR_SAVING_USER_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def getMenteeDetails(request):
    log('Entered mentor details endpoint',1)
    try:
        mentee = Mentee.objects.get(id=decryptData(request.data['id']))
        if not mentee.is_email_verified:
            log("Email not verified",2)
            return Response({'message':EMAIL_NOT_VERIFIFED},status=STATUSES['BAD_REQUEST'])
        serializer = MenteeSerializer(data=request.data)
        valid = serializer.is_valid()
        if(valid):
            mentee.first_name=request.data['first_name']
            mentee.last_name=request.data['last_name']
            mentee.country=request.data['country']
            mentee.phone_number=request.data['phone_number']
            mentee.languages=request.data['languages']
            mentee.gender=request.data['gender']
            mentee.date_of_birth=request.data['date_of_birth']
            mentee.city=request.data['city']
            mentee.areas_of_interest=request.data['areas_of_interest']
            mentee.profile_picture_url=request.data['profile_picture_url']
            mentee.description=request.data['description']
            mentee.role=request.data['role']
            mentee.organization=request.data['organization'],
            mentee.is_experience=request.data['is_experience']

            mentee.save()
            log("success",1)
            return Response({'message':USER_DETAILS_SAVED},status=STATUSES['SUCCESS'])
        else:
            log('invalid details '+str(serializer.errors),2)
            return Response({'message':INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log("Error saving mentor details - "+str(e),3)
        return Response({'message':ERROR_SAVING_USER_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])



def verifyMailSampleTemplate(request):
    return render(request, 'template/index.html',{'BASE_URL':'http://localhost:5000/'})







# log("Invalid user_role",3)
#             return JsonResponse({'message' : INVALID_ROLE},status = STATUSES['BAD_REQUEST'])
            

       

#         print(user)

#         if not user:
#                     # Request entered were user not exist
#             if user_role == 'mentor':
#                 log("User Not Found",2)
#                 return JsonResponse({'message' : USER_NOT_FOUND }, status = STATUSES['BAD_REQUEST'])
            
#             else :
#                 log("User Not Found",2)
#                 return JsonResponse({'message' :USER_NOT_FOUND},status = STATUSES['BAD_REQUEST'])
            
#         if check_password(password, user.password):
#         # if (password == user.password):
#             token = AccessToken.for_user(user)
#             log("User Logged In",1)
#             return JsonResponse({
#                 'message': LOGIN_SUCCESS,  # Using 'message' key
#                 'token': str(token),
#                 'data' : {
#                     'name' : user.first_name + user.last_name,
#                     'email' : email,
#                     'role' : user_role
#                 }
#             }, status= STATUSES['SUCCESS'])
        
#         else:
#             log("Invalid Credentials",3)
#             return JsonResponse({'message' : INVALID_CREDENTIALS}, status = STATUSES['BAD_REQUEST'])
            
#     except Exception as ex:
#         print(ex)
#         log('Error while Login  ' + str(ex),3)
#         return JsonResponse({'message' : LOGIN_ERROR}, status = STATUSES['INTERNAL_SERVER_ERROR'])



    # cur = connection.cursor()
    # cur.execute("INSERT INTO static_mentor (email_id,password) values(\'dharun.ap2022cse@sece.ac.in\',\'ehllo\');")
    # Mentor.objects.raw("INSERT INTO static_mentors (email,password) values(dharun.ap2022cse@sece.ac.in,ehllo);")