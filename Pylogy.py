#Author: Blastomussa
#Date: 1/7/22
import secrets
import requests
from requests_oauthlib import OAuth1

class Pylogy:
    def __init__(self,api_key,secret):
        self.api_key = api_key
        self.secret = secret

    # REST Methods
    def _get(self,uri):
        headeroauth = OAuth1(self.api_key,self.secret,signature_method='PLAINTEXT')
        return requests.get(uri, auth=headeroauth)

    def _post(self,uri,data):
        headeroauth = OAuth1(self.api_key,self.secret,signature_method='PLAINTEXT')
        return requests.post(uri, json=data, auth=headeroauth)

    def _put(self,uri,data):
        headeroauth = OAuth1(self.api_key,self.secret,signature_method='PLAINTEXT')
        return requests.post(uri, json=data, auth=headeroauth)

    def _delete(self,uri):
        headeroauth = OAuth1(self.api_key,self.secret,signature_method='PLAINTEXT')
        return requests.delete(uri, auth=headeroauth)


    # Schoology API calls
    def view_user(self,id):
        uri = 'https://api.schoology.com/v1/users/{0}'.format(id)
        return self._get(uri)


    def delete_user(self,id):
        uri = 'https://api.schoology.com/v1/users/{0}?email_notification=0'.format(id)
        return self._delete(uri)


    def get_user_id(self,email,users=None):
        if(not users): users = self.list_users()
        for user in users:
            if(user['primary_email'] == email): return user['id']
        return "No Schoology ID found for: {}".format(email)


    def list_users(self,role_id=None):
        uri = 'https://api.schoology.com/v1/users?limit=150'
        if(role_id): uri += "&role_ids={}".format(role_id)
        response = self._get(uri).json()
        if('do not exist' not in response):
            users = response['user']
            links = response['links']
            try:
                while(links['next'] != ''):
                    uri = links['next']
                    response = self._get(uri).json()
                    links = response['links']
                    u = response['user']
                    users += u # append paginated results to users json
            except KeyError: pass   # no next page will throw KeyError
            return users
        else:
            return "Role {} does not exist.".format(role_id)


    def create_user(self, user):
        uri = 'https://api.schoology.com/v1/users'
        return self._post(uri,user)

    def create_parent_association(self, student_suid, parent_suid):
        uri = 'https://api.schoology.com/v1/users/import/associations/parents'
        association = {
            'associations':  {
                'association': {
                    "student_school_uid" : student_suid,
                    "parent_school_uid": parent_suid
                }
            }
        }
        return self._post(uri,association)

    def delete_parent_association(self, student_suid, parent_suid):
        uri = 'https://api.schoology.com/v1/users/import/associations/parents'
        association = {
            'associations':  {
                'association': {
                    "student_school_uid" : student_suid,
                    "parent_school_uid": parent_suid,
                    "delete": 1
                }
            }
        }
        return self._post(uri,association)

    # Author specific class methods
    def create_parent(self, fname, lname, email):
        # school_uid should be sufficiently random to prevent collisionsq
        school_uid = lname.lower() + fname.lower() + "_" + secrets.token_hex(4)

        # cleanup text
        s = school_uid.replace(" ","") #no spaces in school_uid
        school_uid = s.encode(encoding="ascii",errors="ignore").decode() #only ascii chars
        email = email.lower() #only lowercase chars emails

        # create and return new user json
        user = {
            'school_uid': school_uid,           #REQUIRED: Needs to be Unique
            'name_first': fname,                #REQUIRED
            'name_last': lname,                 #REQUIRED
            'primary_email': email,             #REQUIRED
            'role_id': 817463,                  #REQUIRED
            'email_login_info': 1,              #NEEDED FOR ONBOARDING
            'tz_offset': -4,
            'tz_name': 'America/New_York',
            'update_existing': 1                #NEEDED
        }
        return self.create_user(user)
