import time
import random
import string
import json
import os 
import bottle
import settings
from Helpers import logger
from EntityManager import EntityManager
from Auth.auth import AuthService, User
from datetime import datetime




#######################################################
# Auth routes
#######################################################
@bottle.route('/login', skip=True)
def login():
    return bottle.template('login.tpl', vd={})


@bottle.route('/login', method='POST', skip=True)
def login():
    e = bottle.request.POST.get('email')
    p = bottle.request.POST.get('password')
    ip = bottle.request.get('REMOTE_ADDR')
    ua = bottle.request.get('HTTP_USER_AGENT')

    error = None

    if e and p:
        a = AuthService(EntityManager())

        session = a.login(e, p, ip, ua)

        if session:
            bottle.response.set_cookie('token', str(session.public_id),\
                                       expires=session.expires,\
                                        httponly=True, path='/')

            # bottle.redirect('/') //this clears cookies
            res = bottle.HTTPResponse("", status=302, Location="/")
            res._cookies = bottle.response._cookies
            return res

        else:
            error = a.errors[0]

    return bottle.template('login.tpl', vd={
            'error':error
        })

@bottle.route('/logout')
def logout():
    a = AuthService(EntityManager())
    a.logout(bottle.request.session)

    bottle.redirect('/')



@bottle.route('/forgotten-password', method='GET', skip=True)
def forgotten_password():
    return bottle.template('forgotten_password', vd={})


@bottle.route('/forgotten-password', method='POST', skip=True)
def forgotten_password():
    e = bottle.request.POST.get('email')

    a = AuthService(EntityManager())
    token = a.generate_password_token(e)

    if token:
        e = Email(recipients=[e])
        body = 'You have requested to reset your password for www.fotodelic.co.uk, please follow this link to reset it:\n\r\n https://%s/reset-password/%s' % (bottle.request.environ['HTTP_HOST'], token)
        e.send('Fotodelic - password reset request', body)               

        return bottle.redirect('/forgotten-password-sent')


    return bottle.template('forgotten_password', vd={
            'error':a.errors[0]
        })



@bottle.route('/forgotten-password-sent', method='GET', skip=True)
def forgotten_password():
    return bottle.template('forgotten_password_sent', vd={})



@bottle.route('/reset-password/:key', method='GET')
def index(key):
    return bottle.template('reset_password', vd={'key':key})


@bottle.route('/reset-password/:key', method='POST', skip=True)
def index(key):
    k = bottle.request.POST.get('key')
    p = bottle.request.POST.get('password')
    p2 = bottle.request.POST.get('password2')
    error = None

    if (p and p2) and (p==p2):
        a = AuthService(EntityManager())
        if a.reset_password(key, p):
            return bottle.redirect('/reset-password-success')

        else:
            error = a.errors[0]

    else:
        error = 'Please enter two matching passwords'


    return bottle.template('reset_password', vd={'error': error})



@bottle.route('/reset-password-success', method='GET', skip=True)
def index():
    return bottle.template('reset_password_success', vd={})






#######################################################



auth_app = bottle.app()

