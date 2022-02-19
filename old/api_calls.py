#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/18/2021
from api_requests import *

def get_user(id):
    api_call = "https://api.schoology.com/v1/users/" + str(id)

    user_json = get_request(api_call)
    return user_json


# role_id is optional filter
def get_users(role_id=""):
    api_call = "https://api.schoology.com/v1/users?limit=150"

    # add to call for filter
    if(role_id != ""):
        api_call = api_call + "&role_ids=" + str(role_id)

    json_data = get_request(api_call)

    # Role does not exist handling
    not_exist = "do not exist"
    if(not_exist in json_data):
        user_jsons = json_data
    else:
        # create list of user jsons
        user_jsons = json_data['user']

        # parse for next page
        links = json_data['links']
        try:
            while(links['next'] != ''):
                api_call = links['next']
                json_data = get_request(api_call)
                links = json_data['links']

                # append paginated results to users json
                u = json_data['user']
                user_jsons = user_jsons + u
        # no next page will throw KeyError
        except KeyError:
            pass

    return user_jsons


def get_inactiveUsers():
    api_call = "https://api.schoology.com/v1/users/inactive"

    json_data = get_request(api_call)
    user_jsons = json_data['user']

    # parse for next page... .update() on dict to join?
    links = json_data['links']
    try:
        while(links['next'] != ''):
            api_call = links['next']
            json_data = get_request(api_call)
            links = json_data['links']

            # append paginated results to users json
            u = json_data['user']
            user_jsons = user_jsons + u
    except KeyError:
        pass

    return user_jsons


def update_user(id,field_json):
    api_call = "https://api.schoology.com/v1/users/" + str(id)

    user_json = put_request(api_call,field_json)
    return user_json


def get_roles():
    api_call = 'https://api.schoology.com/v1/roles'
    json_data = get_request(api_call)
    role_jsons = json_data['role']
    return role_jsons


def get_role(role_id):
    api_call = 'https://api.schoology.com/v1/roles/' + str(role_id)
    role_json = get_request(api_call)
    return role_json


def get_school():
    api_call = "https://api.schoology.com/v1/schools"
    json_data = get_request(api_call)
    school_json = json_data['school']
    return school_json


def create_user(user_json):
    api_call = "https://api.schoology.com/v1/users"

    user_json = post_request(api_call,user_json)
    return user_json


def delete_user(id):
    api_call = 'https://api.schoology.com/v1/users/' + str(id) + "&email_notification=1"

    json_data = delete_request(api_call)
    return json_data


def create_parentAssociation(association_json):
    api_call = "https://api.schoology.com/v1/users/import/associations/parents"

    json_data = post_request(api_call,association_json)
    if(json_data == ""): json_data = "Association failed..check json"
    return json_data


# takes email as arg and returns Schoology ID if found
def get_userID(email):
    users = get_users()
    id = ""
    for user in users:
        if(user['primary_email'] == email):
            id = user['id']
            break
    if(id == ""): id = "No Schoology ID found for: " + email
    return id


# get school user id
# ADD id as optional arg
def get_userSUID(email,users):
    school_uid = ""
    for user in users:
        if(user['primary_email'] == email):
            school_uid = user['school_uid']
            break
    if(school_uid == ""): school_uid = "No School ID found for: " + email
    return school_uid
