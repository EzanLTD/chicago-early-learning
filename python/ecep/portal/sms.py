"""
This module contains classes and utilities for interacting with SMS messages
"""

import logging
import re
from django.views.generic import View
from django.utils.decorators import classonlymethod
from models import Location
from twilio.twiml import Response
from django_twilio.decorators import twilio_view

def enum(**enums):
    """Utility method for nice Enum syntax"""
    return type('Enum', (), enums)

class SmsMessage(object):
    """
    Object representing an SMS message
    """
    body = None
    from_phone = None
    to_phone = None
    to_country = None
    to_state = None
    to_city = None
    to_zip = None

    def __init__(self, request):
        """
        Creates an SMS object from an HttpRequest object (assumed to have come from
        Twilio, see http://www.twilio.com/docs/api/twiml/sms/twilio_request)
        Handles both POST and GET requests
        request: a Django HttpRequest object
        """
        if request is None:
            raise Exception("request was None")

        params = request.REQUEST
        if params is None:
            raise Exception("No POST or GET params provided")

        self.body = params['Body']
        self.from_phone = params['From']
        self.to_phone = params['To']
        self.to_country = params.get('ToCountry', None)
        self.to_state = params.get('ToState', None)
        self.to_city = params.get('ToCity', None)
        self.to_zip = params.get('ToZip', None)


class Conversation(object):
    """
    Represents the state of an sms "Conversation"

    """

    # List of pks into models.Location, represents locations near this user
    locations = None
    zipcode = None
    current_state = None    # type Conversation.State 
    last_msg = None         # type SmsMessage

    def __init__(self, request):
        """
        Creates a new Converstation object, using data stored in request.session if available
        request: a Django HttpRequest object
        """
        s = request.session
        self.current_state = s.get('state', Conversation.State.INIT)
        self.locations = s.get('locations', [])
        self.zipcode = s.get('zipcode', None)
        try:
            self.last_msg = SmsMessage(request)
        except Exception as e:
            logger.debug(
                "Tried to create a Conversation from a request, " + 
                "but couldn't get SmsMessage object.  " + 
                "Request was: %s, Exception was: %s" % 
                (request.get_full_path(), e))

    def update_session(self, session):
        """
        Updates session with the info saved in this object
        Requires django.contrib.sessions.middleware.SessionMiddleware to be enabled
        session: a django HttpRequest.session object
        """
        session['state'] = self.current_state
        session['locations'] = self.locations

# Enum representing the current state of the conversation
Conversation.State = Conversation.enum(INIT=1, GOT_ZIP=2)


class Sms(View):
    """
    View class for handling SMS messages from twilio
    """
    _re_zip = re.compile(r"^\s*(\d{5})\s*$")
    _re_help = re.compile(r"^\s*help\s*$", re.IGNORECASE)
    _re_num = re.compile(r"^\s*(\d{1,2})\s*$")

    USAGE = """
        To get this message text "help"
        Text a 5 digit zipcode to get a list of nearby schools. 
        Text a number on the list to get more information.
        """
    ERROR = 'Sorry, I didn\'t understand that. Please text "help" for instructions'
    FATAL = 'We\'re sorry, something went wrong with your request! Please try again'

    @classonlymethod
    def as_view(cls, **initkwargs):
        # twilio_view doesn't play nice with View classes, so we insert it manually here
        return twilio_view(super(Sms, cls).as_view(**initkwargs))

    @staticmethod
    def reply(msg):
        """Simple wrapper for returning a text message response"""
        r = Response()
        r.sms(msg)
        return r

    def get(self, request):
        """Handler for GET requests, see View.dispatch"""
        result = self.handle_sms(request)
        return result
                
    def post(self, request):
        """Handler for POST requests, see View.dispatch"""
        result = sms(request)
        return self.handle_sms(request)

    def handle_sms(self, request):
        """Main request handler for SMS messages"""
        conv = Conversation(request)
        msg = conv.last_msg
        response = None

        if msg is None:
            return Sms.reply(Sms.FATAL)
            
        matches = Sms._re_zip.match(msg.body)
        if matches is not None:
            # parse zipcodes
            zipcode = matches.groups()[0]
            conv.zipcode = zipcode
            # TODO: get real nearby location pks
            locations = [ 1, 2, 3 ] 
            conv.locations = locations

            if len(locations) > 0:
                conv.current_state = Conversation.State.GOT_ZIP
                # TODO: use real locations
                response = """Schools near %s:
                    1. Foo school
                    2. Bar school
                    3. Baz school
                    """ % zipcode
                conv.update_session(request.session)
            else:
                response = "Sorry, I couldn't find any schools near %s" % zipcode
        if Sms._re_help.match(msg.body):
            # parse "help" requests
            response = Sms.USAGE
        elif conv.current_state == Conversation.State.GOT_ZIP:
            # parse location selection
            matches = Sms._re_num.match(msg.body)
            loc = conv.locations or []
            length = len(loc)
            if matches is not None:
                idx = int(matches.groups()[0]) - 1
                if idx < 0 or idx >= length:
                    response = "Sorry, I don't know about that school near zipcode %s. Please text a number between 1 and %d or a 5 digit zipcode" % (conv.zipcode, idx)
                else:
                    # TODO: return real details
                    response = "idx was %d, details for school go here"
            else:
                response = "Sorry, I didn't understand that number for zipcode %s. Please text a number between 1 and %d, or a 5 digit zipcode" % (conv.zipcode, length)
        else:
            err = "Illegal state in Conversation class. State was %s" % conv.current_state
            logger.debug(err)
            raise ValueError(err)
            
        return Sms.reply(response)

