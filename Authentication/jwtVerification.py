from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken
from static.models import Mentee,Mentor,AuthToken
from static.message_constants import STATUSES,TOKEN_TIMEDOUT,INVALID_TOKEN,VALID_TOKEN

def get_or_create_jwt (user_data,user_role,email) :
    print(user_data , "  " , user_role)
    token = None
    
    if user_role == 'mentor':
        print("Entered if")
        mentor = Mentor.objects.filter(email_id=email).first()
        referenceId = mentor.id
    else:
        print("Entered else")
        mentee = Mentee.objects.filter(email_id = email).first()
        # referenceId = Mentee.objects.get(user = user_data).id
        referenceId = mentee.id

    existing = AuthToken.objects.filter(referenceId = referenceId).first()
    
    #  new user
    if existing is None :
        print("he is a new user ")
        
        access_token = AccessToken.for_user(user_data)

        newToken = AuthToken.objects.create(
        user_type = user_role,
        referenceId=referenceId,
        jwt_token = str(access_token),
    )
        newToken.save()

        token = access_token

    # Existing User
    else :
        print("He is old user")

        token = existing.jwt_token
        existing.created_date = timezone.now().date() 

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

# use the below to verify the jwt token

def validate_token(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        if authorization_header.startswith('Bearer '):
            access_token = authorization_header.split(' ')[1]
        else:
            access_token = authorization_header

        auth_token = AuthToken.objects.filter(jwt_token=access_token).first()
        if auth_token is None:
            return Response({'detail': 'Invalid or expired token'}, status=403)
    else:
        return Response({'detail': 'Authorization header is missing'}, status=403)
            

# import jwt
# from rest_framework.response import Response
# from django.conf import settings

# def validate_token(request):
#     authorization_header = request.headers.get('Authorization')
    
#     if not authorization_header:
#         return Response({'detail': 'Authorization header is missing'}, status=403)
    
#     if authorization_header.startswith('Bearer '):
#         access_token = authorization_header.split(' ')[1]
#     else:
#         access_token = authorization_header
    
#     try:
#         # Decode the token
#         payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
#     except jwt.ExpiredSignatureError:
#         return Response({'detail': 'Token has expired'}, status=403)
#     except jwt.InvalidTokenError:
#         return Response({'detail': 'Invalid token'}, status=403)
    
#     # Check if token exists in AuthToken model
#     auth_token = AuthToken.objects.filter(jwt_token=access_token).first()
#     if auth_token is None:
#         return Response({'detail': 'Token is not valid for any token type'}, status=403)
    
#     return None  # Valid token, continue processing