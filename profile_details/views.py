from static.models import Mentee,Mentor,Experience,RequestedSession,BookedSession,Session
from rest_framework.response import Response
from rest_framework.decorators import api_view
from static.message_constants import STATUSES,ERROR_GETTING_MENTOR_DETAILS,SUCESS,NO_DATA_AVAILABLE,ERROR_SENDING_DETAILS,SESSION_EXISTS
from .assets import urlShortner,log
from static.cipher import encryptData,decryptData

from datetime import datetime

@api_view(['GET'])
def listAllMentors(request):
    log("Entered list Mentors",1)
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
            value['profile_picture_url']=urlShortner(mentor.profile_picture_url) # implementing url shortner
            value['languages']=mentor.languages
            value['name'] = mentor.first_name + " " + mentor.last_name
            value['role'] = mentor.designation
            value['organization'] = mentor.company
            value['experience'] = mentor.mentor_experience
            # checking for mentor tags like toprated and exclusive
            if mentor.is_top_rated:
                value['tag'] = 'TopRated'
            elif mentor.is_experience:
                value['tag'] = 'Exclusive'
            else:
                value['tag'] = None
            
            data.append(value)

        log("Mentors listed successfully",1)
        return Response({'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        log("Error in list mentors"+str(e), 3)
        return Response({'message':ERROR_GETTING_MENTOR_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['GET'])
def menteeDetails(request,id):
    log("Entered mentee details",1)
    try:
        # getting the requested mentee details from the table
        id = decryptData(id)
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
        log("Mentee details provided sucessfully",1)
        return Response({'message':SUCESS,'data':data},status=STATUSES['SUCCESS'])
    except Exception as e:
        # print(e)
        log("Error fetching mentee details"+str(e),1)
        return Response({'message':ERROR_SENDING_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def listMentorsOfMentee(request):
    try:
        
        menteeID = decryptData(request.data['id'])
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
                        'id':encryptData(session.mentor_id)
                    })
        # listing the mentor details as the response
        return Response({"message":SUCESS,"data":mentor_list},status=STATUSES['SUCCESS'])
    except Exception as e:
        # print(e)
        log("Error fetching mentor details"+str(e),1)
        return Response({"message":ERROR_SENDING_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])


