from django.core.mail import send_mail
import pyshorteners
import logging
import inspect
from django.template.loader import render_to_string,get_template
from static.message_constants import DEBUG_CODE,WARNING_CODE,ERROR_CODE

def urlShortner(url):
    short_url = pyshorteners.Shortener().tinyurl.short(url) # using tinyURL service to shorten the url from the pyShortner
    return short_url

def sendVerificationMail(url, email_id):
    print(url)
    template = get_template('template/index.html').render({'BASE_URL':'https://growbinar-backend-4.onrender.com/','verifyMail':url})
    send_mail(
        subject="Verify your mail by clicking the below link",  # subject in the sending mail
        from_email="admin@growbinar.com",                       # sender mail
        html_message= template,                                 # html template
        message='https://growbinar-backend-4.onrender.com/'+url,# message in the mail
        recipient_list=[email_id,]                              # recipient mail id
    )
    print("mail sent")

def sessionBookedMail(email_id,role,userDetails):
    if role=='mentor':
        template = f"You accepted the session of mentee {userDetails['name']} on {userDetails['date']}"
    else:
        template = f"Mentor {userDetails['name']} accepted your request for the session on {userDetails['date']}"
    send_mail(
        subject="Your session has been sucessfully booked",  # subject in the sending mail
        from_email="admin@growbinar.com",                       # sender mail
        # html_message= template,                                 # html template
        message=template,# message in the mail
        recipient_list=[email_id,]                              # recipient mail id
    )
    print("mail sent")

def log(message,code):
    logger = logging.getLogger("Authentication")
    # this inspect.stack provides the funcion name which called this log
    message = str(inspect.stack()[1][3])+" message - "+message
    if code==DEBUG_CODE:
        logger.debug(message)
    elif code==WARNING_CODE:
        logger.warn(message)
    elif code==ERROR_CODE:
        logger.error(message)


# renge wise check
