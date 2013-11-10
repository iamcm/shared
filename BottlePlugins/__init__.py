import bottle
from FormBinder import Types

class ViewdataPlugin(object):
    name = 'viewdata'
    api  = 2

    def __init__(self, callback_function=None, bottle_app_reference=None ):
        self.callback_function = callback_function

    def apply(self, callback, route):
        def wrapper(*a, **ka):
            vd = {}

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
            if self.environment == 'live' or self.environment == 'beta':
                if self.protocol == 'https':
                    if bottle.request.environ.get('HTTP_HTTPS') != 'on':
                        return bottle.redirect(bottle.request.url.replace('http://','https://'))

                elif self.protocol == 'http':
                    if bottle.request.environ.get('HTTP_HTTPS') != 'off':
                        return bottle.redirect(bottle.request.url.replace('https://','http://'))

            return callback(*a, **ka)

        return wrapper