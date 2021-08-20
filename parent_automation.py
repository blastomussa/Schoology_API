#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/18/2021
# Automates parent account creation and student associations in Schoology
import csv
import random
from api_calls import *

# set PowerSchool export path
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    EXPORT = config['PATH']['PS_EXPORT']
except configparser.Error:
    print("Configuration Error...config.ini not found")
    exit()
except KeyError:
    print("Configuration Error...config.ini not found")
    exit()


# PASSED TEST
def build_parent(parent_email,first_name,last_name):
    parent_roleID = 817463

    # should be sufficiently random to prevent collisions
    rand = int(random.random()*10000)
    school_uid = last_name + first_name + "_" + str(rand)

    user = {
        'school_uid': school_uid,           #REQUIRED: Needs to be Unique
        'name_first': first_name,           #REQUIRED
        'name_last': last_name,             #REQUIRED
        'primary_email': parent_email,      #REQUIRED
        'role_id': parent_roleID,           #REQUIRED
        'email_login_info': 1,              #NEEDED
        'tz_offset': -4,
        'tz_name': 'America/New_York',
        'update_existing': 1                #NEEDED
    }

    return user


# PASSED TEST
# returns nothing if failed or bad data
def build_association(student_email="",parent_email="", student_id="",parent_id=""):

    if((student_id == "") and (parent_id == "")):
        student_id = get_userSUID(student_email)
        parent_id = get_userSUID(parent_email)

    # needs to be this specific format per Schoology API docs
    # school_uid NOT uid
    association = {
        'associations':  {
            'association': {
                "student_school_uid" : student_id,
                "parent_school_uid": parent_id
            }
        }
    }

    return association


# get student dict from Schoology with email as key and school_uid as value
def get_students():
    # build student dictionary; need school_uid for parent association json
    # student role id: 817462
    students = get_users(role_id=817462)
    student_dict = {}
    for student in students:
        s_email = student['primary_email']
        s_suid = student['school_uid']
        student_dict[s_email] = s_suid

    return student_dict


# get parent dict from Schoology with email as key and school_uid as value
def get_parents():
    # build parent dictionary; need school_uid for parent association json
    # student role id: 817463
    parents = get_users(role_id=817463)
    parents_dict = {}
    for parent in parents:
        p_email = parent['primary_email']
        p_suid = parent['school_uid']
        parent_dict[p_email] = p_suid

    return student_dict


# PASSED TEST
# get association from PS export, return list of dicts of unique parents that
# can be used to build new users jsons
def get_PSParents():
    emails = []
    data = []
    with open(EXPORT, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parent = {
                'LC_email': row['U_DEF_EXT_STUDENTS.contact1_email'],
                'first_name': row['U_DEF_EXT_STUDENTS.contact1_fname'],
                'last_name': row['U_DEF_EXT_STUDENTS.contact1_lname']
            }
            data.append(parent)
            emails.append(row['U_DEF_EXT_STUDENTS.contact1_email'])

    unique_emails = set(emails)

    parents = []
    for email in unique_emails:
        for parent in data:
            if(email == parent['LC_email']):
                p = {
                    'LC_email': parent['LC_email'],
                    'first_name': parent['first_name'],
                    'last_name': parent['last_name']
                }
                parents.append(p)
                # stop further matches on that email address
                email = None

    return parents


#PASSED TEST
# Builds dictionary with student email as key and parent email as value
def get_PSassociation():
    with open(EXPORT, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        ass = {}
        for row in reader:
            ass[row['U_DEF_EXT_STUDENTS.student_email']] = row['U_DEF_EXT_STUDENTS.contact1_email']

    return ass



def test():




if __name__ == '__main__':
    test()
