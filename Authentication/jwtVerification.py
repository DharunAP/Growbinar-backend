from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken
from core.models import Mentee,Mentor,AuthToken
from core.message_constants import STATUSES,TOKEN_TIMEDOUT,INVALID_TOKEN,VALID_TOKEN,EMAIL_NOT_VERIFIFED,DETAILS_NOT_ENTERED
import pytz
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from datetime import datetime


def is_token_expired(token):
    try:
        decoded_token = AccessToken(token)
        exp_timestamp = decoded_token['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=pytz.utc)
        return exp_datetime < datetime.now(pytz.utc)
    except (TokenError, InvalidToken) as e:
        return True


def checkUserStatus(user,userType):
    if not user.is_email_verified:
        return Response({'message':EMAIL_NOT_VERIFIFED,'role':userType},status=STATUSES['BAD_REQUEST'])
    if user.first_name == None:
        return Response({'message':DETAILS_NOT_ENTERED,'role':userType},status=STATUSES['BAD_REQUEST'])
    return None

def getUserDetails(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        if authorization_header.startswith('Bearer '):
            jwt = authorization_header.split(' ')[1]
        else:
            jwt = authorization_header
    else:
        return {'type':'No header Found'}
    authToken = AuthToken.objects.filter(jwt_token= jwt)[0]
    if authToken==None:
        return {'type':'Invalid User'}
    # print(authToken.jwt_token)
    user = None
    if authToken.user_type=='mentor':
        print(authToken.referenceId,' ref id')
        user = Mentor.objects.get(id = authToken.referenceId)
    elif authToken.user_type=='mentee':
        print(authToken.referenceId,'mentee ref id')
        user = Mentee.objects.get(id = authToken.referenceId)
    return {'type':authToken.user_type,'id':authToken.referenceId,'user':user}


def get_or_create_jwt(user_data, user_role, email):
    print(user_data, "  ", user_role)
    token = None

    if user_role == 'mentor':
        print("Entered if")
        mentor = Mentor.objects.filter(email_id=email).first()
        referenceId = mentor.id
    else:
        print("Entered else")
        mentee = Mentee.objects.filter(email_id=email).first()
        referenceId = mentee.id

    existing = AuthToken.objects.filter(referenceId=referenceId, user_type=user_role).first()
    print(existing, 'this is length of existing--')

    # Check if the token exists and is not expired
    if existing:
        if is_token_expired(existing.jwt_token):
            print("Token is expired, deleting the existing token")
            existing.delete()
            existing = None
        else:
            print("Token is valid")
            existing.created_date = timezone.now().date()
            existing.save()
            token = existing.jwt_token

    # If there is no existing valid token, create a new one
    if existing is None:
        print("Creating a new token for the user")
        access_token = AccessToken.for_user(user_data)
        newToken = AuthToken.objects.create(
            user_type=user_role,
            referenceId=referenceId,
            jwt_token=str(access_token),
        )
        newToken.save()
        token = access_token

    return token


def jwt_verification(request_Token):
    print(request_Token)
    print("Entered jwt_verification")

    existing = AuthToken.objects.filter(jwt_token=request_Token).first()

    if existing is None:
        return Response({
            'message': INVALID_TOKEN
        }, status=STATUSES['INTERNAL_SERVER_ERROR'])

    token_age_days = (timezone.now().date() - existing.created_date).days

    if token_age_days > 7:
        print("Token has expired")
        print(token_age_days, " days since creation")
        existing.delete()
        return Response({
            'message': TOKEN_TIMEDOUT
        }, status=STATUSES['INTERNAL_SERVER_ERROR'])

    print("The token is up-to-date")
    return Response({
        'message': VALID_TOKEN,
        "user_id": existing.referenceId,
    }, status=STATUSES['SUCCESS'])



def validate_token(request):
    authorization_header = request.headers.get('Authorization')
    
    if authorization_header:
        if authorization_header.startswith('Bearer '):
            access_token = authorization_header.split(' ')[1]
        else:
            access_token = authorization_header
        
        try:
            auth_token = AuthToken.objects.get(pk=access_token)
            return None 
        except AuthToken.DoesNotExist:
            return Response({'detail': 'Not a valid user'}, status=403)
    else:
        return Response({'detail': 'Authorization header is missing'}, status=403)
