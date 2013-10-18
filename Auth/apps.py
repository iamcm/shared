import time
import random
import string
import json
import os 
import bottle
import settings
from Helpers import logger
from EntityManager import EntityManager
from Auth.auth import AuthService, User, AuthPlugin, login_form, forgotten_password_form, reset_password_form
from datetime import datetime
from BottlePlugins import FormBinderPlugin
from Helpers.emailHelper import Email

form_binder_plugin = FormBinderPlugin()
auth_plugin = AuthPlugin(EntityManager())

app = bottle.Bottle()

#######################################################
# Auth routes
#######################################################
@app.route('/login')
def login():
    viewdata = {
        'form':login_form().get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Login')
    }
    return bottle.template('login.tpl', vd=viewdata)


@app.route('/login', method='POST', apply=[form_binder_plugin], form=login_form)
def login():
    form = bottle.request.form

    ip = bottle.request.get('REMOTE_ADDR')
    ua = bottle.request.get('HTTP_USER_AGENT')

    error = None

    if form.is_valid():
        u = form.entity
        a = AuthService(EntityManager())

        session = a.login(u.email, u.password, ip, ua)

        if session:
            bottle.response.set_cookie('token', str(session.public_id),\
                                       expires=session.expires,\
                                        httponly=True, path='/')

            # bottle.redirect('/') //this clears cookies
            res = bottle.HTTPResponse("", status=302, Location="/")
            res._cookies = bottle.response._cookies
            return res

        else:
            form.errors.append(a.errors[0])


    viewdata = {
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Login')
    }

    return bottle.template('login.tpl', vd=viewdata)


@app.route('/logout', apply=[auth_plugin])
def logout():
    a = AuthService(EntityManager())
    a.logout(bottle.request.session)

    bottle.redirect('/')



@app.route('/forgotten-password', method='GET')
def forgotten_password():
    viewdata = {
        'form':forgotten_password_form().get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit')
    }

    return bottle.template('forgotten_password', vd=viewdata)


@app.route('/forgotten-password', method='POST', apply=[form_binder_plugin], form=forgotten_password_form)
def forgotten_password():
    form = bottle.request.form

    if form.is_valid():
        e = form.entity.email
        a = AuthService(EntityManager())
        token = a.generate_password_token(e)

        if token:
            e = Email(recipients=[e])
            body = 'You have requested to reset your password for www.fotodelic.co.uk, please follow this link to reset it:\n\r\n https://%s/auth/reset-password/%s' % (bottle.request.environ['HTTP_HOST'], token)
            e.send('Fotodelic - password reset request', body)               

            return bottle.redirect('/auth/forgotten-password-sent')

        else:
            form.errors.append(a.errors[0])

    return bottle.template('forgotten_password', vd={
            'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit')
        })



@app.route('/forgotten-password-sent', method='GET')
def forgotten_password():
    return bottle.template('forgotten_password_sent', vd={})



@app.route('/reset-password/:key', method='GET', apply=[form_binder_plugin], form=reset_password_form)
def index(key):
    form = bottle.request.form
    form.entity.key = key
    
    viewdata={
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit')
    }

    return bottle.template('reset_password', vd=viewdata)


@app.route('/reset-password/:key', method='POST', apply=[form_binder_plugin], form=reset_password_form)
def index(key):
    form = bottle.request.form

    if form.is_valid():
        a = AuthService(EntityManager())
        if a.reset_password(form.entity.key, form.entity.password):
            return bottle.redirect('/auth/reset-password-success')

        else:
            form.errors.append(a.errors[0])

    
    return bottle.template('reset_password', vd={
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit')
    })



@app.route('/reset-password-success', method='GET')
def index():
    return bottle.template('reset_password_success', vd={})






#######################################################



auth_app = app

