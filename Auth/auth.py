from datetime import datetime, timedelta
from BaseModel import BaseModel
from Crypto.Hash import SHA
import random
import string

class User(BaseModel):

    def __init__(self):
        self.email = None
        self.password = None
        self.password_token = None
        self.salt = None
        self.valid = False
        self.api_key = None
        self.added = None

    def _presave(self, entityManager):
        if not self.added:
            self.added = datetime.now()



class Session(BaseModel):

    def __init__(self):
        self.public_id = None
        self.user_id = None
        self.ip = None
        self.useragent = None
        self.added = None
        self.expires = None
        self.valid = True
        self.duration = 168 # number of hours that a session is valid for

    def _presave(self, entityManager):
        if not self.added:
            self.added = datetime.now()

    def _postsave(self, entityManager):
        if not self.public_id:
            # Hash the mongo session id so we can store it in a cookie.
            # By doing this users shouldnt be able to simply increment
            # their 'token' cookie value and gain access to someone elses
            # session
            h = SHA.new()
            h.update(str(self._id))
            self.public_id = h.hexdigest()

            entityManager.save('Session', self)



class AuthService:
    def __init__(self, entityManager):
        self.em = entityManager
        self.errors = None


    def encrypt_password(self, password, salt):
        h = SHA.new()
        h.update(password + salt)
        return h.hexdigest()



    def login(self, email, password, ip, useragent):
        users = self.em.find('User',{'email':email})

        if users:
            user = users[0]

            password = self.encrypt_password(password, user.salt)

            if not user.valid:
                self.errors = ['Account not valid']
                return None

            elif password == user.password:
                session = self.create_session(user._id, ip, useragent)

                return session


        self.errors = ['Matching account not found']
        return None


    def create_session(self, user_id, ip, useragent):
        s = Session()
        s.user_id = user_id
        s.ip = ip
        s.useragent = useragent

        now = datetime.utcnow()
        delta = timedelta(hours=s.duration)
        s.expires = now + delta

        return self.em.save('Session', s)


    def generate_password_token(self, email):
        users = self.em.find('User', {'email':email})
        if len(users)==1:
            u = users[0]
            u.password_token = ''.join(random.sample(string.letters, 30))
            
            self.em.save('User', u)

            return u.password_token

        self.errors = ['Matching account not found']
        return False


    def generate_api_key(self, user_id):
        u = self.em.find_one('User', {'_id':user_id})
        if u:
            u.api_key = ''.join(random.sample(string.letters, 40))
            
            self.em.save('User', u)

            return u.api_key

        self.errors = ['Matching account not found']
        return False


    def reset_password(self, password_token, new_password):
        users = self.em.find('User', {'password_token':password_token})
        if len(users)==1:
            u = users[0]
            u.salt = ''.join(random.sample(string.letters, 15))
            u.password = self.encrypt_password(new_password, u.salt)

            self.em.save('User', u)

            return True

        self.errors = ['Invalid password token']
        return False


    def logout(self, session):
        session.valid = False

        return self.em.save('Session', session)


    def check_session(self, session_id, ip, useragent):
        sessions = self.em.find('Session',{
            'public_id':session_id, 
            'ip':ip,
            'useragent':useragent,
            'valid':True
            })

        if sessions:
            session = sessions[0]
        else:
            self.errors = ['No valid session found']
            return False
        
        if session.expires < datetime.utcnow():
            self.errors = ['Session expired']
            return False

        else:
            now = datetime.utcnow()
            delta = timedelta(hours=session.duration)

            session.expires = now + delta

            self.em.save('Session', session)

            return session

