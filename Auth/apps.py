# coding=utf-8
import time
import random
import string
import json
import os 
import bottle
import settings
from Helpers import logger
from mongorm.EntityManager import EntityManager
from Auth.auth import AuthService, User, AuthPlugin, login_form, forgotten_password_form, reset_password_form, register_form
from datetime import datetime
from FormBinder import FormBinderPlugin
from Helpers.emailHelper import Email
from BottlePlugins import ForceProtocolPlugin

form_binder_plugin = FormBinderPlugin()
auth_plugin = AuthPlugin(EntityManager())
force_https_plugin = ForceProtocolPlugin(environment=settings.ENVIRONMENT)

app = bottle.Bottle()

#######################################################
# Auth routes
#######################################################   
@app.route('/login', apply=[force_https_plugin])
def login():
    viewdata = {
        'form':login_form().get_html(form_class='', row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Login', submit_container_class='')
    }
    return bottle.template('login.tpl', vd=viewdata)


@app.route('/login', method='POST', apply=[force_https_plugin,form_binder_plugin], form=login_form)
def login():
    if getattr(settings, 'LOGIN_SUCCESS_URL', None):
        login_success_url = settings.LOGIN_SUCCESS_URL
    else:
        login_success_url = '/'

    form = bottle.request.form

    ip = bottle.request.get('REMOTE_ADDR')
    ua = bottle.request.get('HTTP_USER_AGENT')

    error = None

    if form.is_valid():
        u = form.hydrate_entity(User())
        a = AuthService(EntityManager())

        session = a.login(u.email, u.password, ip, ua)

        if session:
            bottle.response.set_cookie('token', str(session.public_id),\
                                       expires=session.expires,\
                                        httponly=True, path='/')

            # bottle.redirect('/') //this clears cookies
            res = bottle.HTTPResponse("", status=302, Location=login_success_url)
            res._cookies = bottle.response._cookies
            return res

        else:
            form.errors.append(a.errors[0])

    if getattr(settings, 'LOGIN_FAILED_EMAIL', None):
        e = Email(recipients=[settings.LOGIN_FAILED_EMAIL])
        body = 'Login failed for username: %s<br /><br />%s' % (bottle.request.POST.get('email','-'), '<br />'.join('%s: %s' % (item[0], item[1]) for item in bottle.request.environ.items()))
        e.send('%s - Login failed' % bottle.request.environ['HTTP_HOST'], body)                               

    viewdata = {
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Login', submit_container_class='')
    }

    return bottle.template('login.tpl', vd=viewdata)


@app.route('/logout', apply=[force_https_plugin, auth_plugin])
def logout():
    a = AuthService(EntityManager())
    a.logout(bottle.request.session)

    bottle.redirect('/')



@app.route('/forgotten-password', apply=[force_https_plugin], method='GET')
def forgotten_password():
    viewdata = {
        'form':forgotten_password_form().get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit', submit_container_class='')
    }

    return bottle.template('forgotten_password', vd=viewdata)


@app.route('/forgotten-password', method='POST', apply=[force_https_plugin, form_binder_plugin], form=forgotten_password_form)
def forgotten_password():
    form = bottle.request.form

    if form.is_valid():
        e = form.get_value('email')
        a = AuthService(EntityManager())
        token = a.generate_password_token(e)

        if token:
            e = Email(recipients=[e])
            body = 'You have requested to reset your password for %s, please follow this link to reset it:\n\r\n https://%s/auth/reset-password/%s' % (bottle.request.environ['HTTP_HOST'], bottle.request.environ['HTTP_HOST'], token)
            e.send('%s password reset request' % bottle.request.environ['HTTP_HOST'], body)               

            return bottle.redirect('/auth/forgotten-password-sent')

        else:
            form.errors.append(a.errors[0])

    return bottle.template('forgotten_password', vd={
            'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit', submit_container_class='')
        })



@app.route('/forgotten-password-sent', apply=[force_https_plugin], method='GET')
def forgotten_password():
    return bottle.template('forgotten_password_sent', vd={})



@app.route('/reset-password/:key', method='GET', apply=[force_https_plugin, form_binder_plugin], form=reset_password_form)
def index(key):
    form = bottle.request.form
    form.set_value('key', key)
    
    viewdata={
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit')
    }

    return bottle.template('reset_password', vd=viewdata)


@app.route('/reset-password/:key', method='POST', apply=[force_https_plugin, form_binder_plugin], form=reset_password_form)
def index(key):
    form = bottle.request.form

    if form.is_valid():
        a = AuthService(EntityManager())
        if a.reset_password(form.get_value('key'), form.get_value('password')):
            return bottle.redirect('/auth/reset-password-success')

        else:
            form.errors.append(a.errors[0])

    
    return bottle.template('reset_password', vd={
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Submit', submit_container_class='')
    })



@app.route('/reset-password-success', apply=[force_https_plugin], method='GET')
def index():
    return bottle.template('reset_password_success', vd={})


@app.route('/register', apply=[force_https_plugin])
def register():
    viewdata = {
        'form':register_form().get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Register', submit_container_class='')
    }
    return bottle.template('register.tpl', vd=viewdata)


@app.route('/register', method='POST', apply=[force_https_plugin,form_binder_plugin], form=register_form)
def register():
    form = bottle.request.form

    if form.is_valid():
        em = EntityManager()
        auth_service = AuthService(em)

        user = auth_service.create_user(form.get_value('email'), form.get_value('password'), form.get_value('username'),True)

        em.save('User', user)

        if getattr(settings, 'REGISTER_SUCCESS_URL', None):
            url = settings.REGISTER_SUCCESS_URL
        else:
            url = '/'

        return bottle.redirect(url)

    viewdata = {
        'form':form.get_html(row_class='form-group', submit_btn_class="btn btn-primary", submit_btn_text='Register', submit_container_class='')
    }
    return bottle.template('register.tpl', vd=viewdata)


@app.route('/register-complete', apply=[force_https_plugin])
def register():
    return bottle.template('register_complete.tpl')



#######################################################



auth_app = app

