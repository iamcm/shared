# coding=utf-8
import json
import bottle
import random
import datetime
import calendar
import string
from FormBinder import Types
from Helpers import aes

class AttributeDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class ViewdataPlugin(object):
    name = 'viewdata'
    api  = 2

    def __init__(self, callback_function=None, bottle_app_reference=None ):
        self.callback_function = callback_function

    def apply(self, callback, route):
        def wrapper(*a, **ka):
            vd = AttributeDict()

            if self.callback_function:
                vd.update(self.callback_function())

            bottle.response.viewdata = vd
            return callback(*a, **ka)

        return wrapper



class ForceProtocolPlugin(object):
    name = 'force_protocol'
    api  = 2

    def __init__(self, protocol='https', environment='live'):
        self.protocol = protocol.lower()
        self.environment = environment.lower()

    def apply(self, callback, route):

        def wrapper(*a, **ka):
            if self.environment == 'live' or self.environment == 'beta' or self.environment == 'production':
                if self.protocol == 'https':
                    if 'HTTP_HTTPS' in bottle.request.environ.keys() and bottle.request.environ.get('HTTP_HTTPS') != 'on'\
                        or 'HTTP_X_FORWARDED_PROTO' in bottle.request.environ.keys() and bottle.request.environ.get('HTTP_X_FORWARDED_PROTO') != 'https':
                        return bottle.redirect(bottle.request.url.replace('http://','https://'))

                elif self.protocol == 'http':
                    if 'HTTP_HTTPS' in bottle.request.environ.keys() and bottle.request.environ.get('HTTP_HTTPS') == 'on'\
                        or 'HTTP_X_FORWARDED_PROTO' in bottle.request.environ.keys() and bottle.request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https':
                        return bottle.redirect(bottle.request.url.replace('https://','http://'))

            return callback(*a, **ka)

        return wrapper



class SessionDataPlugin(object):
    name = 'session_data'
    api  = 2

    def __init__(self, name='sc'):
        self.name = name

    def apply(self, callback, route):

        def wrapper(*a, **ka):
            #decrypt after request
            if self.name in bottle.request.cookies.keys():
                value = bottle.request.get_cookie(self.name)
                c = aes.Cipher()
                try:
                    bottle.request.session_data = json.loads(c.decrypt(value))
                except ValueError:
                    pass
            else:
                timestamp = str(calendar.timegm(datetime.datetime.now().timetuple()))
                randomstring = ''.join(random.sample(string.letters + string.digits, 32))
                combinedid = timestamp + randomstring
                bottle.request.session_data = {'_id':combinedid}

            body = callback(*a, **ka)

            #encrypt before response
            if bottle.request.session_data is not None:
                c = aes.Cipher()
                enc = c.encrypt(json.dumps(bottle.request.session_data))
                bottle.response.set_cookie(self.name, enc, path='/')


            print bottle.request.session_data

            return body

        return wrapper