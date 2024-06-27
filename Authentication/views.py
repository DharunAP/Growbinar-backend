from django.shortcuts import render, redirect
from static.models import Mentee,Mentor,Experience,AuthToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from static.cipher import encryptData,decryptData
from static.message_constants import LOGIN_SUCCESS,INVALID_ROLE,LOGIN_ERROR,INVALID_CREDENTIALS,STATUSES,USER_NOT_FOUND
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import MentorSerializer,MenteeSerializer,UserSerializer
from static.message_constants import STATUSES,INVALID_CREDENTIALS,DETAILS_NOT_ENTERED,ERROR_VERIFYING_USER_EMAIL,USER_CREATED,EMAIL_EXISTS,SIGNUP_ERROR,VERIFIED_USER_EMAIL,ERROR_VERIFYING_USER_EMAIL,USER_DETAILS_SAVED,ERROR_SAVING_USER_DETAILS,EMAIL_NOT_VERIFIFED,ACCESS_DENIED
from static.routes import VERIFY_MENTOR_ROUTE,VERIFY_MENTEE_ROUTE
from django.contrib.auth.hashers import make_password,check_password
from .assets import sendVerificationMail,log
from .jwtVerification import get_or_create_jwt, getUserDetails, validate_token, checkUserStatus
from rest_framework.permissions import IsAuthenticated
from static.message_constants import DEBUG_CODE,WARNING_CODE,ERROR_CODE


@api_view(['POST'])
def user_login(request):
    print("Request has Entered into User Login Page")
    log("Entered User-Login ",DEBUG_CODE)

    try:
        print(request.data)
        email = request.data.get('email_id')
        password = request.data.get('password')
        user_role = request.data.get('user_role')  # 'mentor' or 'mentee'
        user = None
        if user_role == 'mentor':
                 # Request entered where the user exist
            print('mentor')
            print(email)
            user = Mentor.objects.filter(email_id=email).first()
            log("User is Mentor",DEBUG_CODE)

        elif user_role == 'mentee':
            print('mentee')
            user = Mentee.objects.filter(email_id=email).first()
            log("User is Mentee",DEBUG_CODE)
            
        else:
            log("Invalid user_role",ERROR_CODE)
            return JsonResponse({'message' : INVALID_ROLE},status = STATUSES['BAD_REQUEST'])
        print(user,'-----')

        if not user:
                    # Request entered were user not exist
            if user_role == 'mentor':
                log("User Not Found",WARNING_CODE)
                return JsonResponse({'message' : USER_NOT_FOUND }, status = STATUSES['BAD_REQUEST'])
            
            else :
                log("User Not Found",WARNING_CODE)
                return JsonResponse({'message' :USER_NOT_FOUND},status = STATUSES['BAD_REQUEST'])
            
        if check_password(password, user.password):
        # if (password == user.password):
            token = str(get_or_create_jwt(user,user_role,email))
            print(token, " tata printed ")
            log("User Logged In",DEBUG_CODE)

            if not user.is_email_verified:  # checking for user email verification
                return Response({'message':EMAIL_NOT_VERIFIFED,'token':token},status=STATUSES['BAD_REQUEST'])
            elif user.first_name is None:   # checking weather user has completed stepper page
                return Response({'message':DETAILS_NOT_ENTERED,'token':token},status=STATUSES['SUCCESS']) 

            return JsonResponse({
                'message': LOGIN_SUCCESS,  # Using 'message' key
                'token' : token,
                'id':encryptData(user.id)
                # 'data' : {
                #     'name' : user.first_name + user.last_name,
                #     'user_id' : encryptData(user.id),  # encoding the user id
                #     'email' : email,
                #     'role' : user_role
                # }
            }, status= STATUSES['SUCCESS'])
        
        else:
            log("Invalid Credentials",ERROR_CODE)
            
            return JsonResponse({'message' : INVALID_CREDENTIALS}, status = STATUSES['BAD_REQUEST'])
            
    except Exception as error:
        print(error)
        log('Error while Login  ' + str(error),ERROR_CODE)
        return JsonResponse({'message' : LOGIN_ERROR,'error':str(error)}, status = STATUSES['INTERNAL_SERVER_ERROR'])




@api_view(['POST'])
def MenteeSignup(request):
    log("Entered mentee-signup",DEBUG_CODE)
    try:
        # chekking weather email already exists
        if Mentee.objects.filter(email_id=request.data['email_id']).exists():
            log("Email already exists as a mentee",DEBUG_CODE)
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
            sendVerificationMail(VERIFY_MENTEE_ROUTE+"?id="+encryptedID,request.data['email_id'])  # sending the verification mail
            jwt_token = get_or_create_jwt(instance, 'mentee', instance.email_id)  # creating jwt token for the user
            log("signup successfull",DEBUG_CODE)
            return Response({'message':USER_CREATED,'id':encryptedID,"jwt_token":str(jwt_token)}, status=STATUSES['SUCCESS'])
        else:
            # sending bad request response for invalid payload
            log("invalid credentails for signup "+str(serializer.errors),WARNING_CODE)
            print(serializer.errors)
            return Response({"message":INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log("Error creating a mentee"+str(e),ERROR_CODE)
        print('error',e)
        return Response({'message':SIGNUP_ERROR,'error':str(e)}, status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def MentorSignup(request):
    log("Entered mentor-signup",DEBUG_CODE)
    try:
        # chekking weather email already exists
        if Mentor.objects.filter(email_id=request.data['email_id']).exists():
            log("Email already exists",WARNING_CODE)
            return Response({"message":EMAIL_EXISTS},status=STATUSES['BAD_REQUEST'])

        serializer = UserSerializer(data=request.data)
        print(request.data)
        # validating the payload
        valid=serializer.is_valid()
        if valid:
            # creating mentor object
            instance = Mentor.objects.create(email_id=request.data['email_id'],password=make_password(request.data['password']))
            instance.save()
            log("signup successfull",DEBUG_CODE)
            encryptedID = encryptData(instance.id)      # encrypting the id to send as the response
            sendVerificationMail(VERIFY_MENTOR_ROUTE+"?id="+encryptedID,request.data['email_id']) # sending the verification mail
            jwt_token = get_or_create_jwt(instance, 'mentor', instance.email_id)  # creating jwt token for the user
            return Response({'message':USER_CREATED,'id':encryptedID,"jwt_token":str(jwt_token)}, status=STATUSES['SUCCESS'])
        else:
            # sending bad request response
            log("invalid credentails for signup",WARNING_CODE)
            print(serializer.errors)
            return Response({"message":INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as error:
        log("Error creating a mentor"+str(error),ERROR_CODE)
        print(error)
        return Response({'message':SIGNUP_ERROR,'error':str(error)}, status=STATUSES['INTERNAL_SERVER_ERROR'])


@api_view(['GET'])
def VerifyMentee(request):
    log('Entered email verification of mentee',DEBUG_CODE)
    try:
        # Getting mentee id from the url and setting is_email_verified to True
        menteeID = decryptData(request.GET.get('id'))
        print(menteeID)
        mentee = Mentee.objects.get(id=menteeID)
        mentee.is_email_verified = True
        mentee.save()
        log('Email verification sucess for '+menteeID,DEBUG_CODE)
        return redirect('https://growbinar.com/mentee')
    except Exception as error:
        log("Error verifying email "+str(error),ERROR_CODE)
        print(error)
        return Response({'message':ERROR_VERIFYING_USER_EMAIL,'error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET'])
def VerifyMentor(request):
    log('Entered email verification mentor',DEBUG_CODE)
    try:
        # Getting mentor id from the url and setting is_email_verified to True
        mentorID = decryptData(request.GET.get('id'))
        mentor = Mentor.objects.get(id=mentorID)
        mentor.is_email_verified = True
        mentor.save()
        log('Email verification sucess for '+mentorID,DEBUG_CODE)
        return redirect('https://growbinar.com/mentor')
        return Response({'message':VERIFIED_USER_EMAIL},status=STATUSES['SUCCESS'])
    except Exception as error:
        log("Error verifying email "+str(error),ERROR_CODE)
        print(error)
        return Response({'message':ERROR_VERIFYING_USER_EMAIL,'error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def getMentorDetails(request):
    log('Entered mentor details endpoint',DEBUG_CODE)
    try:
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response

        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentor':  # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})   
        print(userDetails['id'])
        mentor = Mentor.objects.get(id=userDetails['id'])
        # mentor = Mentor.objects.get(id = decryptData(request.data['id']))
        print(mentor)
        if not mentor.is_email_verified:
            log("Email not verified",WARNING_CODE)
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
            mentor.mentor_experience=request.data['MentorExperience']
            mentor.designation=request.data['designation']
            mentor.company=request.data['company']

            mentor.save()
            log("success",DEBUG_CODE)
            return Response({'message':USER_DETAILS_SAVED},status=STATUSES['SUCCESS'])
        else:
            log('invalid details '+str(serializer.errors),WARNING_CODE)
            return Response({'message':INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as error:
        log("Error saving mentor details - "+str(error),ERROR_CODE)
        print('final',error)
        return Response({'message':ERROR_SAVING_USER_DETAILS,'error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def getMenteeDetails(request):
    log('Entered mentor details endpoint',DEBUG_CODE)
    try:
        print('here ')
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentee':      # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})
        print(userDetails['id'])
        mentee = Mentee.objects.get(id=userDetails['id'])
        # mentee = Mentee.objects.get(id = decryptData(request.data['id']))
        if not mentee.is_email_verified:
            log("Email not verified",WARNING_CODE)
            return Response({'message':EMAIL_NOT_VERIFIFED},status=STATUSES['BAD_REQUEST'])
        serializer = MenteeSerializer(data=request.data)
        valid = serializer.is_valid()
        print(request.data['organization'])
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
            mentee.organization=request.data['organization']
            mentee.is_experience=request.data['is_experience']

            mentee.save()
            log("success",DEBUG_CODE)
            return Response({'message':USER_DETAILS_SAVED},status=STATUSES['SUCCESS'])
        else:
            log('invalid details '+str(serializer.errors),WARNING_CODE)
            return Response({'message':INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as error:
        log("Error saving mentor details - "+str(error),ERROR_CODE)
        print(error)
        return Response({'message':ERROR_SAVING_USER_DETAILS,'error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET'])
def user_logout(request):
    try:
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            if authorization_header.startswith('Bearer '):
                access_token = authorization_header.split(' ')[1]
            else:
                access_token = authorization_header

            print("The access token that we need", access_token)

            # Delete the token from the database
            auth_token = AuthToken.objects.filter(jwt_token=access_token).first()
            if auth_token:
                auth_token.delete()
                # Return a success response
                return JsonResponse({'message': 'Logout successful'}, status=STATUSES['SUCCESS'])
            else:
                return JsonResponse({'message': 'Token not found'}, status=STATUSES['INTERNAL_SERVER_ERROR'])
        else:
            # If no token is provided in the request headers, return an error response
            return JsonResponse({'message': 'Token is required 👎🏻'}, status=STATUSES['INTERNAL_SERVER_ERROR'])
    except Exception as e:
        # If an exception occurs, return an error response
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
def checkUserDetails(request):
    try:
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentor' and userDetails['type']!='mentee':      # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
            userChecking = checkUserStatus(userDetails['user'],userDetails['type'])
            if(userChecking is not None):
                return userChecking
            return Response({'message':'Perfect go ahead','role':userDetails['type']},status=STATUSES['SUCCESS'])
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})
    except Exception as error:
        return Response({'message':'Error checking the user status.','error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

def verifyMailSampleTemplate(request):
    return render(request, 'template/index.html',{'BASE_URL':'http://localhost:8000/'})

@api_view(['GET'])
def resendMail(request):
    try:
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})
        print(userDetails['id'])
        if userDetails['type']=='mentee':
            email = Mentee.objects.get(id = userDetails['id']).email_id
            sendVerificationMail(VERIFY_MENTEE_ROUTE+"?id="+encryptData(userDetails['id']),email)  # sending the verification mail
        else:
            email = Mentor.objects.get(id = userDetails['id']).email_id
            sendVerificationMail(VERIFY_MENTOR_ROUTE+"?id="+encryptData(userDetails['id']),email)  # sending the verification mail
        return Response({'message':'Mail sent successfully'},status=STATUSES['SUCCESS'])
    except Exception as error:
        print(error)
        return Response({'message':'Error sending mail','error':str(error)},status=STATUSES['INTERNAL_SERVER_ERROR'])

# def verifyMailSampleTemplate(request):
#     return render(request, 'template/index.html',{'BASE_URL':'http://localhost:8000/'})


# log("Invalid user_role",ERROR_CODE)
#             return JsonResponse({'message' : INVALID_ROLE},status = STATUSES['BAD_REQUEST'])
            

# Login:
# error for email no token
# no error for stepper - 200

# common
# no token _> login
# no stepper -> 400

       

#         print(user)

#         if not user:
#                     # Request entered were user not exist
#             if user_role == 'mentor':
#                 log("User Not Found",WARNING_CODE)
#                 return JsonResponse({'message' : USER_NOT_FOUND }, status = STATUSES['BAD_REQUEST'])
            
#             else :
#                 log("User Not Found",WARNING_CODE)
#                 return JsonResponse({'message' :USER_NOT_FOUND},status = STATUSES['BAD_REQUEST'])
            
#         if check_password(password, user.password):
#         # if (password == user.password):
#             token = AccessToken.for_user(user)
#             log("User Logged In",DEBUG_CODE)
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
#             log("Invalid Credentials",ERROR_CODE)
#             return JsonResponse({'message' : INVALID_CREDENTIALS}, status = STATUSES['BAD_REQUEST'])
            
#     except Exception as ex:
#         print(ex)
#         log('Error while Login  ' + str(ex),ERROR_CODE)
#         return JsonResponse({'message' : LOGIN_ERROR}, status = STATUSES['INTERNAL_SERVER_ERROR'])



    # cur = connection.cursor()
    # cur.execute("INSERT INTO static_mentor (email_id,password) values(\'dharun.ap2022cse@sece.ac.in\',\'ehllo\');")
    # Mentor.objects.raw("INSERT INTO static_mentors (email,password) values(dharun.ap2022cse@sece.ac.in,ehllo);")
