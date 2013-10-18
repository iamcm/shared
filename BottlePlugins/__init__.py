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



class FormBinderPlugin(object):
    name = 'form_binder'
    api  = 2

    def __init__(self):
        self.form  = None

    def apply(self, callback, route):
        self.form = route.config.get('form')

        def wrapper(*a, **ka):
            form = self.form()
            instance = form.entity
            for formitem in form.formitems:
                if bottle.request.params.get(formitem.name):
                    if formitem.type == 'int':
                        try:
                            setattr(instance, formitem.name, int(bottle.request.params.get(formitem.name)))
                        except:
                            pass

                    elif formitem.type == 'list_int':
                        try:
                            setattr(instance, formitem.name, [int(i) for i in bottle.request.params.getall(formitem.name)])
                        except:
                            pass

                    elif formitem.type == 'list_string':
                        try:
                            setattr(instance, formitem.name, [str(i) for i in bottle.request.params.getall(formitem.name)])
                        except:
                            pass

                    else:
                        try:
                            setattr(instance, formitem.name, str(bottle.request.params.get(formitem.name)))
                        except:
                            pass

            bottle.request.form = form

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