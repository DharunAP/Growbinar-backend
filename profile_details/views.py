from static.models import Mentee,Mentor,Experience,RequestedSession,BookedSession,Session,Testimonial
from rest_framework.response import Response
from rest_framework.decorators import api_view
from static.message_constants import STATUSES,INVALID_CREDENTIALS,DETAILS_NOT_ENTERED,ERROR_VERIFYING_USER_EMAIL,ERROR_GETTING_MENTOR_DETAILS,SUCESS,NO_DATA_AVAILABLE,ERROR_SENDING_DETAILS,SESSION_EXISTS,ACCESS_DENIED
from .assets import urlShortner,log
from static.cipher import encryptData,decryptData
from .serializers import TestimonialSerializer
from Authentication.jwtVerification import *
from static.message_constants import DEBUG_CODE,WARNING_CODE,ERROR_CODE

from datetime import datetime

def get_datetime(entry):
    date_str = entry["date"]
    time_str = entry["from"]
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

def getAvailableSessions(id):
    availabeSession = AvailabeSession.objects.filter(mentor_id = id)
    if(not availabeSession.exists()):
        return []
    upComming_sessions = []
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    # looping in the array to get only the upcomming sessions        
    for session in availabeSession[0].availableSlots:
        if current_date<=datetime.strptime(session['date'], '%Y-%m-%d').date(): # date checking
            if current_date == datetime.strptime(session['date'], '%Y-%m-%d').date(): 
                if current_time>datetime.strptime(session['from'],'%H:%M:%S').time(): # time checking for same date
                    continue
            upComming_sessions.append(session)

    sorted_data = sorted(upComming_sessions, key=get_datetime)
    return sorted_data

@api_view(['GET'])
def listAllMentors(request):
    log("Entered list Mentors",DEBUG_CODE)
    try:
        # getting required fields from the mentor table for each mentor
        mentors = Mentor.objects.raw("SELECT id,profile_picture_url,is_top_rated,is_experience,languages,first_name,last_name,designation,company,mentor_experience FROM static_mentor;")
        data = []
        print('hi',len(mentors))
        # iterating through the query set to convert each instance to an proper list 
        for mentor in mentors:
            if(mentor.first_name==None):
                continue
            value = dict()
            value['mentor_id']=encryptData(mentor.id)
            value['profile_picture_url']=mentor.profile_picture_url # implementing url shortner
            value['languages']=mentor.languages
            value['name'] = mentor.first_name + " " + mentor.last_name
            value['role'] = mentor.designation
            value['organization'] = mentor.company
            value['experience'] = mentor.mentor_experience
            # slots = AvailabeSession.objects.filter(mentor=mentor)
            value['avaliableSession'] = getAvailableSessions(mentor.id)
            # if slots.exists():
            #     value['avaliableSession'] = slots[0].availableSlots 
            # else:
            #     value['availableSession'] = []
            # checking for mentor tags like toprated and exclusive
            if mentor.is_top_rated:
                value['tag'] = 'TopRated'
            elif mentor.is_experience:
                value['tag'] = 'Exclusive'
            else:
                value['tag'] = None
            print(value,'--')
            data.append(value)

        log("Mentors listed successfully",DEBUG_CODE)
        print(data)
        return Response({'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log("Error in list mentors"+str(e), ERROR_CODE)
        return Response({'message':ERROR_GETTING_MENTOR_DETAILS,'error':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET'])
def menteeDetails(request):
    log("Entered mentee details",DEBUG_CODE)
    try:
        # getting the requested mentee details from the table
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            userChecking = checkUserStatus(userDetails['user'],userDetails['type'])
            if(userChecking is not None):
                return userChecking
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})   
        print(userDetails['id'])

        try :
            id = decryptData(request.data['id'])
        except:
            id = userDetails['id']
        mentee = Mentee.objects.raw(f"SELECT id,is_experience,first_name,last_name,languages,role,organization,profile_picture_url,city,is_experience,description,areas_of_interest FROM static_mentee WHERE id={id};")[0]
        
        # urlShortner(mentee.profile_picture_url) # implementing url shortner
        experience = Experience.objects.raw(f"SELECT id,company,from_duration,to_duration FROM static_Experience WHERE referenced_id={mentee.id} and role_type=\'mentee\'")
        experience_list = []
        # iterating through the experience to list it
        for i in experience:
            value = dict()
            value['institution_name'] = i.company
            value['Date'] = {
                'startDate':i.from_duration,
                'endDate':i.to_duration
            }
            experience_list.append(value)
        data = {
            "name":mentee.first_name+" "+mentee.last_name,
            "languages":mentee.languages,
            "location":mentee.city,
            "overview":mentee.description,
            "areas_of_interest":mentee.areas_of_interest,
            "experience":experience_list
        }
        # background languages experience
        log("Mentee details provided sucessfully",DEBUG_CODE)
        return Response({'message':SUCESS,'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log("Error fetching mentee details"+str(e),ERROR_CODE)
        return Response({'message':ERROR_SENDING_DETAILS,'error':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def listMentorsOfMentee(request):
    try:
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentee':      # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
            userChecking = checkUserStatus(userDetails['user'],userDetails['type'])
            if(userChecking is not None):
                return userChecking
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})
        print(userDetails['id'])
        menteeID = userDetails['id']
        # getting the requested sessions of the mentee
        request_sessions = RequestedSession.objects.raw(f'SELECT session_id,mentee_id,is_accepted from static_RequestedSession where mentee_id={menteeID};')
        if(len(request_sessions)<1): # check if there is some data or not
            return Response({"message":NO_DATA_AVAILABLE},status=STATUSES['SUCCESS'])

        mentor_list = []
        for index in request_sessions:
            # getting the session object of each requested sesssion 
            session = Session.objects.raw(f'SELECT id,mentor_id,is_booked from static_session where id={index.session_id}')[0]
            if session.is_booked:
                # if session is booked then get booked sessions details
                booked_session = BookedSession.objects.raw(f"SELECT id,is_completed from static_BookedSession where requested_session_id={index.session_id}")
                if(len(booked_session)<1):
                    continue
                if booked_session[0].is_completed:
                    # if the session is completed then add the mentor details to the list
                    mentor_list.append({
                        'mentor_id':encryptData(session.mentor_id)
                    })
        # listing the mentor details as the response
        return Response({"message":SUCESS,"data":mentor_list},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log("Error fetching mentor details"+str(e),ERROR_CODE)
        return Response({"message":ERROR_SENDING_DETAILS,'error':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET','POST'])
def testimonials(request):
    log('Entered testimonials endpoint',DEBUG_CODE)
    if(request.method=='GET'):
        try:
            testimonial_data = Testimonial.objects.all()
            data = []
            for index in testimonial_data:
                value = dict()
                value['mentor'] = {'name':index.mentor.first_name+" "+index.mentor.last_name,'role':index.mentor.designation}
                value['mentee'] = {'name':index.mentee.first_name+" "+index.mentee.last_name,'role':index.mentee.role}
                value['content'] = index.content
                data.append(value)
            return Response({'data':data},status=STATUSES['SUCCESS'])
        except Exception as e:
            print(e)
            return Response({'message':'Error getting testimonials'},status=STATUSES['INTERNAL_SERVER_ERROR'])
    try:
        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response

        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentee':  # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
            userChecking = checkUserStatus(userDetails['user'])
            if(userChecking is not None):
                return userChecking
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})   
        print(userDetails['id'])
        # request.data['mentor'] = r
        request.data['mentor'] = int(decryptData(request.data['mentor']))
        request.data['mentee'] = int(decryptData(request.data['mentee']))
        serializer = TestimonialSerializer(data=request.data)
        if(serializer.is_valid()):
            instance = Testimonial.objects.create(
                mentor_id= request.data['mentor'],
                mentee_id= request.data['mentee'],
                content= request.data['content']
            )
            instance.save()
            return Response({'message':'Testimonial created sucessfully.'},status=STATUSES['SUCCESS'])
        print(serializer.errors)
        return Response({'message':INVALID_CREDENTIALS},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        print(e)
        return Response({'message':'Error creating testimonial','error':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])




# Guhan code

from static.models import Mentor,Experience,AvailabeSession,Mentee,UserQuery
from rest_framework.decorators import api_view,permission_classes
from static.message_constants import STATUSES,USER_NOT_FOUND,FETCHING_ERROR,MENTOR_DETAILS,SESSION_EXISTS,QUERY_SUBMITTED,QUERY_EMPTY
from .assets import log
from rest_framework.decorators import api_view
from django.http import JsonResponse
from static.cipher import decryptData,encryptData
from Authentication.jwtVerification import validate_token
from datetime import datetime
from Authentication.jwtVerification import validate_token
from rest_framework.permissions import IsAuthenticated
import pyshorteners

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def mentor_details(request):
    try:

        validation_response = validate_token(request)  # validating the requested user using authorization headder
        if validation_response is not None:
            return validation_response
        try:
            userDetails = getUserDetails(request)  # getting the details of the requested user
            if userDetails['type']!='mentor':      # chekking weather he is allowed inside this endpoint or not
                return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
            userChecking = checkUserStatus(userDetails['user'],userDetails['type'])
            if(userChecking is not None):
                return userChecking
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})
        print(userDetails['id'])

        # mentor_id = decryptData(id) # decoding of the id 
        mentor_id = userDetails['id']
        print('mentor - id',mentor_id,'----')

        log("Entered mentor details",DEBUG_CODE)
        print("Request in mentor_details")
        print(request.data)
        
        mentor = Mentor.objects.raw(f"SELECT id,first_name,last_name,designation,company,languages,bio,is_email_verified,city FROM static_mentor WHERE id={mentor_id};")[0]
        try:
            availabeSession = AvailabeSession.objects.get(mentor_id = mentor_id)
        except:
            availabeSession = {'availableSlots':[]}
        print('----avai-----',availabeSession)
        # print(mentor.is_email_verified)
        log("mentor email verified",DEBUG_CODE)
        # experience = Experience.objects.raw(f"SELECT id,company,from_duration,to_duration,role FROM static_Experience WHERE referenced_id={mentor.id};")[0]
        # availabeSessions_list = list(availabeSession.values('mentor','availableSlots'))

        data = {
            "name":mentor.first_name+" "+mentor.last_name,
            "location":mentor.city,
            "organisation" : mentor.company,
            "languages" : mentor.languages,
            # "experience" : {
            #     'role' : experience.role,
            #     'date' : {
            #         'startDate' : experience.from_duration,
            #         'endDate' : experience.to_duration
            #     }
            # },
            "overview":mentor.bio,
            'background' : {
                'expertise' : mentor.areas_of_expertise,
                'fluency' : mentor.languages
            },
            "Available-Sessions" :availabeSession['availableSlots']
        }
        # background languages experience
        log("Mentor details provided sucessfully",DEBUG_CODE)
        return JsonResponse({'message' : MENTOR_DETAILS,
                             'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log('Error while fetching details',ERROR_CODE)
        return JsonResponse({'message' : FETCHING_ERROR,'error':str(e)},status = STATUSES['INTERNAL_SERVER_ERROR'])



# @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# def createAvailableSession(request):
#     log('Entered create available session endpoint ',DEBUG_CODE)
#     try:
#         print(decryptData(request.data['id']),"---------")

#         #for verifying the token
#         validation_response = validate_token(request)  # validating the requested user using authorization headder
#         if validation_response is not None:
#             return validation_response
#         try:
#             userDetails = getUserDetails(request)  # getting the details of the requested user
#             if userDetails['type']!='mentor':      # chekking weather he is allowed inside this endpoint or not
#                 return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
#             userChecking = checkUserStatus(userDetails['user'])
#             if(userChecking is not None):
#                 return userChecking
#         except Exception as error:
#             print(error)
#             return Response({'message':'Error authorizing the user try logging in again'})
#         print(userDetails['id'])


#         availabeSession = AvailabeSession.objects.filter(mentor_id = userDetails['id'])
#         print(availabeSession)
#         if availabeSession.exists():
#             # update code
#             conflictingSlots = []
#             newSlots = availabeSession[0].availableSlots
#             # checking weather the slot already exists in the table
#             for slot in request.data['availableSlots']:
#                 print(slot)
#                 if slot in newSlots:
#                     conflictingSlots.append(slot)
#                     continue
#                 # adding the slot to the array
#                 date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
#                 from_time = datetime.strptime(slot['from'], '%H:%M:%S').time()
#                 to_time = datetime.strptime(slot['to'], '%H:%M:%S').time()
#                 newSlots.append({
#                     "date":str(date),
#                     "from":str(from_time),
#                     "to":str(to_time)
#                 })
            
#             # adding the new slots to the table
#             availabeSession.update(availableSlots = newSlots)
#             log('New slots crated sucessfully ',DEBUG_CODE)
#             return JsonResponse({'message':SESSION_EXISTS,"conflicted slots":conflictingSlots},status=STATUSES['SUCCESS'])

#         # creating new available session for the mentor
#         print('hi')
#         slots = []
#         for slot in request.data['availableSlots']:
#             date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
#             from_time = datetime.strptime(slot['from'], '%H:%M:%S').time()
#             to_time = datetime.strptime(slot['to'], '%H:%M:%S').time()
#             slots.append({
#                 "date":str(date),
#                 "from":str(from_time),
#                 "to":str(to_time)
#             })
#         print(slots)
#         instance = AvailabeSession.objects.create(
#             mentor_id = decryptData(request.data['id']),
#             availableSlots = slots
#         )
#         instance.save()
#         log("New session created sucessfully ",DEBUG_CODE)
#         return JsonResponse({"message":"Successfully created","slots":slots},status=STATUSES['SUCCESS'])
#     except Exception as e:
#         print(e)
#         log("Error in creating available session "+str(e),ERROR_CODE)
#         return JsonResponse({'message':""},status=STATUSES['INTERNAL_SERVER_ERROR'])
    

@api_view(['GET'])
def listAllMentees(request):
    log("Entered list Mentee",DEBUG_CODE)
    try:
        # getting required fields from the mentor table for each mentor
        mentee = Mentee.objects.raw("SELECT id,first_name,last_name,country,city,phone_number,email_id,profile_picture_url,areas_of_interest FROM static_mentee;")
        data = []
        print('hi',len(mentee))
        # iterating through the query set to convert each instance to an proper list 
        for mentee in mentee:
            if(mentee.first_name==None):
                continue
            value = dict()
            value['mentee_id']=encryptData(mentee.id)
            value['profile_picture_url']=pyshorteners.Shortener().tinyurl.short(mentee.profile_picture_url) # implementing url shortner
            value['name'] = mentee.first_name + " " + mentee.last_name
            value['role'] = mentee.role
            value['email-id'] = mentee.email_id
            value['organization'] = mentee.organization
            value['areas_of_interest'] = mentee.areas_of_interest
            value['country'] = mentee.country
            value['date_of_birth'] = mentee.date_of_birth
            value['city'] = mentee.city
            
            data.append(value)

        log("Mentees listed successfully",DEBUG_CODE)
        return JsonResponse({'message':'Mentee List Displayed',
                             'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        log("Error in list mentors"+str(e), ERROR_CODE)
        return JsonResponse({'message':'error','error':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])
    

@api_view(['POST'])
def userQuery (request):
    print('In query View')
    try :
        log('Enter query form',DEBUG_CODE)
        name = request.data['name']
        from_email = request.data['email']
        to_email = 'growbinar@gmail.com'
        phone_number = request.data['phone_number']
        query = request.data['query']
        log('Got the inputs',DEBUG_CODE)
        if query :
            user_query = UserQuery(
                name=name,
                from_email=from_email,
                to_email=to_email,
                phone_number=phone_number,
                query=query
            )

            user_query.save()
            log('Query saved and returned',DEBUG_CODE)
            return JsonResponse({'message': QUERY_SUBMITTED}, status=STATUSES['SUCCESS'])

        else :
            log('Query filed is missing',2)
            return JsonResponse({'message': QUERY_EMPTY}, status=STATUSES['SUCCESS'])

    except Exception as ex :
        log('Error in query',ERROR_CODE)
        return JsonResponse({'message' : 'Some Error Occured','error' : str(ex)},status = STATUSES['INTERNAL_SERVER_ERROR'])