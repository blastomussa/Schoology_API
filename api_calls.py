#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/18/2021
from api_requests import *

# PASSED TEST
def get_user(id):
    api_call = "https://api.schoology.com/v1/users/" + str(id)

    user_json = get_request(api_call)
    return user_json


# PASSED TEST
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


# PASSED TEST
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
    api_call = ''

    roles_json = get_request(api_call)
    return roles_json



def get_role(role_id):
    api_call = ''

    role_json = get_request(api_call)
    return role_json



def get_school():
    api_call = ''

    school_json = get_request(api_call)
    return school_json



def create_user(user_json):
    api_call = "https://api.schoology.com/v1/users"

    user_json = post_request(api_call,user_json)
    return user_json


# PASSED TEST
def delete_user(id):
    api_call = 'https://api.schoology.com/v1/users/' + str(id) + "&email_notification=1"

    json_data = delete_request(api_call)
    return json_data


# --------->>> I need to test parent associations POST
def create_parentAssociation(parent_json):
    api_call = ''

    json_data = get_request(api_call)
    return json_data


# test call
def test():
  pass



if __name__ == '__main__':
    test()
