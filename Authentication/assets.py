from django.core.mail import send_mail
import pyshorteners
import logging
import inspect
from django.template.loader import render_to_string,get_template

def urlShortner(url):
    short_url = pyshorteners.Shortener().tinyurl.short(url) # using tinyURL service to shorten the url from the pyShortner
    return short_url

def sendVerificationMail(url, email_id):
    print(url)
    template = get_template('template/index.html').render({'BASE_URL':'http://localhost:5000/','verifyMail':url})
    send_mail(
        subject="Verify your mail by clicking the below link",  # subject in the sending mail
        from_email="admin@growbinar.com",                       # sender mail
        html_message= template,                                 # html template
        message='http://localhost:5000/'+url,                   # message in the mail
        recipient_list=[email_id,]                              # recipient mail id
    )
    print("mail sent")


def log(message,code):
    logger = logging.getLogger("Authentication")
    # this inspect.stack provides the funcion name which called this log
    message = str(inspect.stack()[1][3])+" message - "+message
    if code==1:
        logger.debug(message)
    elif code==2:
        logger.warn(message)
    elif code==3:
        logger.error(message)



# renge wise check