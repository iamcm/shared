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

    def __init__(self, bottle_app_reference, protocol='HTTPS'):
        self.bottle = bottle_app_reference
        self.protocol = protocol

    def apply(self, callback, route):

        def wrapper(*a, **ka):
            if self.protocol.lower() == 'https':
                if self.bottle.request.environ.get('HTTP_HTTPS') == 'on':
                    return self.bottle.redirect(self.bottle.request.url.replace('https://','http://'))

            elif self.protocol.lower() == 'http':
                if self.bottle.request.environ.get('HTTP_HTTPS') == 'off':
                    return self.bottle.redirect(self.bottle.request.url.replace('http://','https://'))

            return callback(*a, **ka)

        return wrapper