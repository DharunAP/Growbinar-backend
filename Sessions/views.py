from django.shortcuts import render
from static.models import AvailabeSession,Session,SessionFeedback,BookedSession,RequestedSession
from rest_framework.response import Response
from rest_framework.decorators import api_view
from static.message_constants import *
from .assets import log
from static.cipher import encryptData,decryptData
from datetime import datetime
from static.message_constants import DEBUG_CODE,WARNING_CODE,ERROR_CODE

from django.http import JsonResponse
from django.utils import timezone
from datetime import date,datetime
from Authentication.jwtVerification import *
from rest_framework.decorators import api_view,permission_classes
from datetime import datetime,date
from .validators import convert_to_hms,is_valid_date,is_valid_time
from rest_framework.permissions import IsAuthenticated
# endpoint to clear data of available slots - cron jobs [independent file]

def get_datetime(entry):
    date_str = entry["date"]
    time_str = entry["from"]
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


@api_view(['GET','POST'])
def createAvailableSession(request):
    log('Entered create available session endpoint for '+request.method,DEBUG_CODE)
    # to provide all the avalilable sessions of the mentor listed up-next
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
        print(userDetails['user'])
        # user = Mentee.objects.get(id = userDetails['id'])
    except Exception as error:
        print(error)
        return Response({'message':'Error authorizing the user try logging in again'})
    print(userDetails['id'])
    if request.method == 'GET':
        try:
            try:
                id = decryptData(request.data['id'])
            except:
                id = userDetails['id']
            availabeSession = AvailabeSession.objects.filter(mentor_id = id)
            if(not availabeSession.exists()):
                return Response({'message':'No session exixts'},status=200)
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
            log('available sessions returned sucessfully',DEBUG_CODE)
            return Response({'data':sorted_data},status=STATUSES['SUCCESS'])
        except Exception as e:
            log('Error returing the available sessions '+str(e),ERROR_CODE)
            return Response({'message':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

    # for post method to strore data
    try:
        # getting the available session object
        availabeSession = AvailabeSession.objects.filter(mentor = userDetails['user'])
        
        if availabeSession.exists():
            # update code
            conflictingSlots = []
            newSlots = availabeSession[0].availableSlots
            
            # checking weather the slot already exists in the table
            for slot in request.data['availableSlots']:
                if slot in newSlots:
                    conflictingSlots.append(slot)
                    continue
                # adding the slot to the array
                date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
                from_time = datetime.strptime(slot['from'], '%H:%M:%S').time()
                to_time = datetime.strptime(slot['to'], '%H:%M:%S').time()
                newSlots.append({
                    "date":str(date),
                    "from":str(from_time),
                    "to":str(to_time)
                })
            
            # adding the new slots to the table
            availabeSession.update(availableSlots = newSlots)
            log('New slots crated sucessfully ',DEBUG_CODE)
            if len(conflictingSlots)!=0:
                return Response({'message':SESSION_EXISTS,"conflicted slots":conflictingSlots},status=STATUSES['BAD_REQUEST'])
            return Response({'message':SESSION_UPDATED},status=STATUSES['SUCCESS'])

        # creating new available session for the mentor
        slots = []
        for slot in request.data['availableSlots']:
            date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
            from_time = datetime.strptime(slot['from'], '%H:%M:%S').time()
            to_time = datetime.strptime(slot['to'], '%H:%M:%S').time()
            slots.append({
                "date":str(date),
                "from":str(from_time),
                "to":str(to_time)
            })
        instance = AvailabeSession.objects.create(
            mentor = userDetails['user'],
            availableSlots = slots
        )
        instance.save()
        log("New session created successfully ",DEBUG_CODE)
        return Response({"message":SUCESS,"slots":slots},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log("Error in creating available session "+str(e),ERROR_CODE)
        return Response({'message':ERROR_SAVING_USER_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])


# @api_view(['POST'])
# def getBookedSession(request):
#     log('Entered get available session endpoint for '+request.method,DEBUG_CODE)
#     # to provide all the avalilable sessions of the mentor listed up-next
#     validation_response = validate_token(request)  # validating the requested user using authorization headder
#     if validation_response is not None:
#         return validation_response
#     try:
#         userDetails = getUserDetails(request)  # getting the details of the requested user
#         if userDetails['type']!='mentor' and userDetails['type']!='mentee':      # chekking weather he is allowed inside this endpoint or not
#             return Response({'message':ACCESS_DENIED},status=STATUSES['BAD_REQUEST'])
#         userChecking = checkUserStatus(userDetails['user'],userDetails['type'])
#         if(userChecking is not None):
#             return userChecking
#         print(userDetails['user'])
#         # user = Mentee.objects.get(id = userDetails['id'])
#     except Exception as error:
#         print(error)
#         return Response({'message':'Error authorizing the user try logging in again'})
#     print(userDetails['id'])
#     try:
#         try:
#             id = decryptData(request.data['id'])
#         except:
#             id = userDetails['id']
#         sessions = Session.objects.filter(mentor_id=id, is_booked=True)


#         return
#     except Exception as error:
#         return

@api_view(['POST'])
def bookSession(request):
    log('Entered booking a session',DEBUG_CODE)
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
        # changeing is_booked to true in sessions table
        session_instance = Session.objects.get(id = request.data['session_id'])
        session_instance.is_booked = True
        session_instance.save()

        # changing the is_accepted of the RequestedSession table to true
        requested_session = RequestedSession.objects.get(session = session_instance)
        requested_session.is_accepted = True
        requested_session.save()

        # creating a bookedSession object
        booked_session = BookedSession.objects.create(
            requested_session = requested_session,
        )
        booked_session.save()
        log('session booked',DEBUG_CODE)
        return Response({'message':'Session booked sucessfully','id':booked_session.id},status=STATUSES['SUCCESS'])
    except Exception as e:
        log('Error booking a session '+str(e),ERROR_CODE)
        return Response({'message':"Error booking a session"},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def sessionCompleted(request):
    try:
        booked_session = BookedSession.objects.get(id=request.data['id'])
        booked_session.is_completed = True
        booked_session.save()
        return Response({"message":'success'},status=STATUSES['SUCCESS'])
    except Exception as e:
        return Response({'message':"error in marking"},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def sessionFeedback(request):

    '''
        docs input, output param 2-3 lines code writer name
    '''
    log('Entered creating session feedback',DEBUG_CODE)
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
        # creating a new feedback object with the requested data
        booked_session = BookedSession.objects.get(id = request.data['bookedSession'])
        if(booked_session.is_completed):
            feedback = SessionFeedback.objects.create(
                booked_session = booked_session,
                description = request.data['description'],
                ratings = request.data['ratings']
            )
            feedback.save()
            log('Feedback created sucessfully',DEBUG_CODE)
            return Response({'message':FEEDBACK_CREATED},status=STATUSES['SUCCESS'])
        else:
            log('Session is not completed',WARNING_CODE)
            return Response({'message':SESSION_NOT_COMPLETED},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log('Error creating session feedback '+str(e),ERROR_CODE)
        return Response({'message':ERROR_CREATING_FEEDBACK},status=STATUSES['INTERNAL_SERVER_ERROR'])



# Guhan code

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def upcoming_sessions(request) :
    log('Entered upcoming session',DEBUG_CODE)
    validation_response = validate_token(request)
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
    mentor_id = userDetails['id'] # decoding the data

    current_date = date.today()           # current date
    current_time = datetime.now().time()  # current time
 
    try :
        # mentor_details = Mentor.objects.filter(id = mentor_id)
        mentor_details = Mentor.objects.raw(f"SELECT id,first_name,last_name,designation,company,profile_picture_url FROM static_mentor WHERE id={mentor_id};")[0]
        print(mentor_details)

        # if mentor_details.exists() :
        if mentor_details :
            # if the mentor Exists
            log("Mentor Exists",DEBUG_CODE)
            # session_details =  Session.objects.filter(mentor = mentor_details.id) # getting the session details with that mentor
            session_details = Session.objects.raw(f"SELECT id,from_slot_time,slot_date FROM static_session WHERE id={mentor_id};")
            
            print('entered the loop --')
            sessions = []  # list to store the upcoming sessions
            for index in session_details:
                value = dict()

                requested_details = RequestedSession.objects.filter(session = index.id)[0]
                if requested_details.is_accepted :
                    log('meeting is accepted',DEBUG_CODE)
                    booked_details = BookedSession.objects.filter(requested_session = requested_details.id)[0]
                    url = booked_details.hosting_url
                    if booked_details.is_completed :
                        stat = MEET_STATUS[202]
                    else :
                        stat = MEET_STATUS[201]

                else :
                    log('meeting is not accepted',DEBUG_CODE)
                    url = "NULL"
                    stat = MEET_STATUS[203]
               
                value['mentee'] = requested_details.mentee.first_name + requested_details.mentee.last_name
                # value['profile-link'] = 'NULL',
                value['role'] = mentor_details.designation
                value['organisation'] = mentor_details.company
                value['time'] = index.from_slot_time
                value['link'] = url
                value['date'] = index.slot_date
                value['status'] = stat
                value['meet_type'] = MEET_TYPE[101]
                
                sessions.append(value)

            log("Upcoming session displayed",DEBUG_CODE)
            print(request.auth," === ", "this is the auth token")
            return JsonResponse({
                "message" : "The details of upcoming session",
                'data' : sessions
            }, status= STATUSES['SUCCESS'])
        
        else :
                # User not found with the id
            log("User not Found",WARNING_CODE)
            return JsonResponse({
                'message' : USER_NOT_FOUND
            }, status = STATUSES['NOT_FOUND'])
        
    except Exception as ex :
        print(ex,"in catch")
            # Error while fetching the details
        log("Error while displaying upcoming session",ERROR_CODE)
        return JsonResponse({
                'message' : FETCHING_ERROR
            }, status = STATUSES['NOT_FOUND'])


# View for creating new Session

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def new_sessions_booking(request):
    try:
        print("hello")

        
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

        start_date = request.data['start_date']
        start_time = request.data['start_time']
        end_time = request.data['end_time']
        mentor_id = decryptData(request.data['mentor_id'])
        # mentor_id = request.data['mentor_id']  # preferred mentor of the mentee
        mentee_id = userDetails['id']
        print(mentor_id, " --- in decrypted format -- ")

    # Validating the time and date
        if not is_valid_date(start_date):
            log("Enter the valid date",ERROR_CODE)
            return JsonResponse({'message': INVALID_DATE}, status= STATUSES['INTERNAL_SERVER_ERROR'])

            # Validate start_time and end_time
        if not is_valid_time(start_time):
            log('Enter the valid time',ERROR_CODE)
            return JsonResponse({'message': INVALID_TIME}, status= STATUSES['INTERNAL_SERVER_ERROR'])
        if not is_valid_time(end_time):
            log('Enter the valid time',ERROR_CODE)
            return JsonResponse({'message': INVALID_TIME}, status= STATUSES['INTERNAL_SERVER_ERROR'])

    #taking the mentor instance
        mentor_ins = Mentor.objects.filter(id=mentor_id)[0]
        print(mentor_ins,"--mentor ins--")
    # checking with available sessions
        available_sessions = AvailabeSession.objects.filter(mentor_id=mentor_id)[0]
        free_slots = [slot for slot in available_sessions.availableSlots if slot['date'] == start_date]  # for taking list for that date
        print(free_slots, "--ithu summa trial tha")

        try:
            converted_start_time = convert_to_hms(start_time)
            converted_end_time = convert_to_hms(end_time)
        except ValueError as e:
            return JsonResponse({'message': str(e)}, status=400)

        users_start_time = datetime.strptime(converted_start_time, '%H:%M:%S').time()
        users_end_time = datetime.strptime(converted_end_time, '%H:%M:%S').time()
        print(free_slots)

        for available in free_slots:
            print('IN free slots loop')
            present_start_time = datetime.strptime(convert_to_hms(available['from']), '%H:%M:%S').time()
            present_end_time = datetime.strptime(convert_to_hms(available['to']), '%H:%M:%S').time()
            
            #checking if the time is between the available time

            if users_start_time == users_end_time:
            # if both time are equal
                log('Start and End time are same',ERROR_CODE)
                return JsonResponse({'message': SAME_TIME}, status=STATUSES['INTERNAL_SERVER_ERROR'])
            
            if users_start_time >= present_start_time and users_end_time <= present_end_time:

                session_details = Session.objects.filter(mentor=mentor_id, slot_date=start_date)
                print(session_details, "-- the session details --")

                if not session_details :
                    log('No already session available ',DEBUG_CODE)
                    new_session = Session.objects.create(
                            mentor=mentor_ins,
                            slot_date=start_date,
                            from_slot_time=users_start_time,
                            to_slot_time=users_end_time
                        )

                    new_session.save()
                    log('New session created',DEBUG_CODE)

                    mentee_ins = Mentee.objects.filter(id=mentee_id)[0]
                    
                    requested_session = RequestedSession.objects.create(
                        session=new_session,  # This will store the ID of the new_session in the requested session
                        mentee=mentee_ins,
                        is_accepted=False
                    )
                    requested_session.save()
                    log('Requestedsession created successfully',DEBUG_CODE)
                    return JsonResponse({'message': NEW_SESSION,
                                         'session_id' : new_session.id}, status=STATUSES['SUCCESS'])
                                        
                flag =False
                for available_time in session_details:

                    print("Entered into the loop of session_details")
                    available_from_time = convert_to_hms(available_time.from_slot_time)
                    print(available_from_time,' 00000 ',users_start_time)
                    available_to_time = convert_to_hms(available_time.to_slot_time)
                    print(available_to_time,' 8888 ',users_end_time)

                    if (users_start_time <= datetime.strptime(available_to_time, '%H:%M:%S').time() and 
                        users_end_time >= datetime.strptime(available_from_time, '%H:%M:%S').time() and 

                        users_start_time >= datetime.strptime(available_from_time, '%H:%M:%S').time() and
                        users_end_time <= datetime.strptime(available_to_time, '%H:%M:%S').time()  and
                        
                        users_start_time == datetime.strptime(available_from_time, '%H:%M:%S').time() and
                        users_end_time == datetime.strptime(available_to_time, '%H:%M:%S').time()) :
                        flag = True

                if flag:
                    log('Session already available',WARNING_CODE)
                    return JsonResponse({'message': BOOKED_SESSION}, status=STATUSES['INTERNAL_SERVER_ERROR'])
                        
                else :

                    new_session = Session.objects.create(
                            mentor=mentor_ins,
                            slot_date=start_date,
                            from_slot_time=users_start_time,
                            to_slot_time=users_end_time
                        )

                    new_session.save()
                    log('Session created successfully',DEBUG_CODE)

                    mentee_ins = Mentee.objects.filter(id=mentee_id)[0]
                    
                    requested_session = RequestedSession.objects.create(
                            session=new_session,  # This will store the ID of the new_session in the requested session
                            mentee=mentee_ins,
                            is_accepted=False
                        )
                    requested_session.save()
                    print(new_session.id)
                    log('Requestedsession created successfully',DEBUG_CODE)
                    return Response({'message': NEW_SESSION,'session_id' : new_session.id}, status=STATUSES['SUCCESS'])

            else:
                log('Enter the wrong time',WARNING_CODE)
                return JsonResponse({'message': WRONG_TIME}, status=STATUSES['INTERNAL_SERVER_ERROR'])

        log('No free slots available',DEBUG_CODE)
        return JsonResponse({'message': UNAVAILABLE_SLOTS}, status=STATUSES['INTERNAL_SERVER_ERROR'])
    
    except Exception as e:
        log('Some error occurred',ERROR_CODE)
        return JsonResponse({'message':'error',
                             'Error' : str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def session_cancellation(request):
    print("Session Cancellation")
    
    try:
        session_id = request.data['session_id']
        user_type = request.data['user_role']
        user_ids = request.data['id']
        user_id = decryptData(user_ids)
        print(type(user_id), '-- the decrypted id is ---')

        
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
        except Exception as error:
            print(error)
            return Response({'message':'Error authorizing the user try logging in again'})

            
        #taking current date and time for checking
        current_datetime = datetime.now().replace(microsecond=0)
        current_date = date.today()

        session_details = Session.objects.get(id=session_id)
        print(session_details, '-- session details --')

        requested_session = RequestedSession.objects.get(session=session_id)
        print(requested_session, '-- requested session --')

        # Calculate the session start datetime
        session_start_datetime = datetime.combine(session_details.slot_date, session_details.from_slot_time)
        print(session_start_datetime, '---- session start datetime ----')

        # if the user is mentee
        if user_type == 'mentee':
            log('User is mentee',DEBUG_CODE)
            mentee_details = Mentee.objects.get(id=user_id)

            if requested_session.mentee_id == int(user_id):
                log('Mentee have access to cancel the session',DEBUG_CODE)
                print('same mentee')
                if requested_session.is_accepted:
                    log('Session has been accepted by mentor',DEBUG_CODE)
                    print('session accepted already')
                    time_difference = (session_start_datetime - current_datetime).total_seconds() #to check time difference

                    if time_difference <= 4 * 3600:
                        log('Due to less than 4hrs session cannot cancelled',WARNING_CODE)
                        return JsonResponse({'message': NO_TIME_SESSION}, status=STATUSES['INTERNAL_SERVER_ERROR'])
                    else:
                        session_details.delete()
                        log('Session cancelled successfully',DEBUG_CODE)
                        return JsonResponse({'message': CANCELLATION_SUCCESS}, status=STATUSES['SUCCESS'])
                else:
                    session_details.delete()
                    log('Session cancelled successfully',DEBUG_CODE)
                    return JsonResponse({'message': CANCELLATION_SUCCESS}, status=STATUSES['SUCCESS'])
            else:
                log("Don't have access to cancel the session",WARNING_CODE)
                return JsonResponse({'message': NO_ACCESS_TO_CANCEL}, status=STATUSES['INTERNAL_SERVER_ERROR'])

        # if the user is mentor
        else:
            log('User is mentor',DEBUG_CODE)
            mentor_details = Mentor.objects.get(id=user_id)

            if session_details.mentor_id == int(user_id):
                log('Mentor have access to cancel the session',DEBUG_CODE)
                if requested_session.is_accepted:
                    print("Session got accepted")
                    log('Session has been accepted by mentor',DEBUG_CODE)
                    if (session_details.slot_date - current_date).days <= 0:
                        log('It is same day',DEBUG_CODE)
                        time_difference = (session_start_datetime - current_datetime).total_seconds()
                        if time_difference <= 4 * 3600:
                            log('Time less than 4hrs',WARNING_CODE)
                            return JsonResponse({'message': NO_TIME_SESSION}, status=STATUSES['INTERNAL_SERVER_ERROR'])
                    else:
                        session_details.delete()
                        log('Session deleted successfully',DEBUG_CODE)
                        return JsonResponse({'message': CANCELLATION_SUCCESS}, status=STATUSES['SUCCESS'])
                else:
                    session_details.delete()
                    log('Session deleted successfully',DEBUG_CODE)
                    return JsonResponse({'message': CANCELLATION_SUCCESS}, status=STATUSES['SUCCESS'])
            else:
                print(' --- mentor_id != user_id --- ')
                log('Mentor had no access to delete the session',WARNING_CODE)
                return JsonResponse({'message': NO_ACCESS_TO_CANCEL}, status=STATUSES['INTERNAL_SERVER_ERROR'])

    except Exception as e:
        log('Error had occured',ERROR_CODE)
        return JsonResponse({'message': "Error Occured", "Error": str(e)}, status=STATUSES['INTERNAL_SERVER_ERROR'])