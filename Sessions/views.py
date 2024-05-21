from django.shortcuts import render
from static.models import AvailabeSession,Session,SessionFeedback,BookedSession,RequestedSession
from rest_framework.response import Response
from rest_framework.decorators import api_view
from static.message_constants import STATUSES,SESSION_NOT_COMPLETED,ERROR_CREATING_FEEDBACK,FEEDBACK_CREATED,ERROR_GETTING_MENTOR_DETAILS,SUCESS,NO_DATA_AVAILABLE,ERROR_SENDING_DETAILS,SESSION_EXISTS,ERROR_SAVING_USER_DETAILS
from .assets import log
from static.cipher import encryptData,decryptData
from datetime import datetime
# endpoint to clear data of available slots - cron jobs [independent file]

def get_datetime(entry):
    date_str = entry["date"]
    time_str = entry["from"]
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


@api_view(['GET','POST'])
def createAvalableSession(request):
    log('Entered create available session endpoint for '+request.method,1)
    # to provide all the avalilable sessions of the mentor listed up-next
    if request.method == 'GET':
        try:
            availabeSession = AvailabeSession.objects.filter(mentor_id = decryptData(request.data['id']))
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
            log('available sessions returned sucessfully',3)
            return Response({'message':sorted_data},status=STATUSES['SUCCESS'])
        except Exception as e:
            log('Error returing the available sessions '+str(e),3)
            return Response({'message':str(e)},status=STATUSES['INTERNAL_SERVER_ERROR'])

    # for post method to strore data
    try:
        # getting the available session object
        availabeSession = AvailabeSession.objects.filter(mentor_id = decryptData(request.data['id']))

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
            log('New slots crated sucessfully ',1)
            return Response({'message':SESSION_EXISTS,"conflicted slots":conflictingSlots},status=STATUSES['SUCCESS'])

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
            mentor_id = decryptData(request.data['id']),
            availableSlots = slots
        )
        instance.save()
        log("New session created successfully ",1)
        return Response({"message":SUCESS,"slots":slots},status=STATUSES['SUCCESS'])
    except Exception as e:
        print(e)
        log("Error in creating available session "+str(e),3)
        return Response({'message':ERROR_SAVING_USER_DETAILS},status=STATUSES['INTERNAL_SERVER_ERROR'])

@api_view(['POST'])
def bookSession(request):
    log('Entered booking a session',1)
    try:
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
        log('session booked',1)
        return Response({'message':'Session booked sucessfully','id':booked_session.id},status=STATUSES['SUCCESS'])
    except Exception as e:
        log('Error booking a session '+str(e),3)
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
    log('Entered creating session feedback',1)
    try:
        # creating a new feedback object with the requested data
        booked_session = BookedSession.objects.get(id = request.data['bookedSession'])
        if(booked_session.is_completed):
            feedback = SessionFeedback.objects.create(
                booked_session = booked_session,
                description = request.data['description'],
                ratings = request.data['ratings']
            )
            feedback.save()
            log('Feedback created sucessfully',1)
            return Response({'message':FEEDBACK_CREATED},status=STATUSES['SUCCESS'])
        else:
            log('Session is not completed',2)
            return Response({'message':SESSION_NOT_COMPLETED},status=STATUSES['BAD_REQUEST'])
    except Exception as e:
        log('Error creating session feedback '+str(e),3)
        return Response({'message':ERROR_CREATING_FEEDBACK},status=STATUSES['INTERNAL_SERVER_ERROR'])

