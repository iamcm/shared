import bottle

class ViewdataPlugin(object):
    name = 'viewdata'
    api  = 2

    def __init__(self, vd={}, callback_function=None, bottle_app_reference=None ):
        self.vd = {}
        self.vd.update(vd)
        self.callback_function = callback_function
        self.bottle_app_reference = bottle_app_reference

    def apply(self, callback, route):

        def wrapper(*a, **ka):
            if self.callback_function:
                self.vd.update(self.callback_function())

            bottle.response.viewdata = self.vd
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