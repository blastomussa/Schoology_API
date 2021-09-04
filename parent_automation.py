#!/usr/bin/env python3
# Author: Blastomussa
# Date 8/18/2021
# Automates parent account creation and student associations in Schoology
# time.sleep() statements keep app from overloading API
import os
import csv
import random
import unidecode
from pymail import *
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


# build parent json that can be used with create_user()
def build_parent(parent_email,first_name,last_name):
    parent_roleID = 817463

    # should be sufficiently random to prevent collisions
    rand = int(random.random()*10000)
    school_uid = last_name.lower() + first_name.lower() + "_" + str(rand)

    # no spaces
    s = school_uid.replace(" ","")

    # ascii only
    school_uid = unidecode.unidecode(s)

    # lowercase emails
    email = parent_email.lower()

    # create and return new user json
    user = {
        'school_uid': school_uid,           #REQUIRED: Needs to be Unique
        'name_first': first_name,           #REQUIRED
        'name_last': last_name,             #REQUIRED
        'primary_email': email,             #REQUIRED
        'role_id': parent_roleID,           #REQUIRED
        'email_login_info': 1,              #NEEDED
        'tz_offset': -4,
        'tz_name': 'America/New_York',
        'update_existing': 1                #NEEDED
    }
    return user


# returns nothing if failed or bad data
# using emails is slow and only works after parent is created in Schoology
def build_association(student_email="",parent_email="", student_suid="",parent_suid=""):

    if((student_suid == "") and (parent_suid == "")):
        users = get_users()
        student_suid = get_userSUID(student_email,users)
        parent_suid = get_userSUID(parent_email,users)

    # needs to be this specific format per Schoology API docs
    # school_uid NOT uid
    association = {
        'associations':  {
            'association': {
                "student_school_uid" : student_suid,
                "parent_school_uid": parent_suid
            }
        }
    }
    return association


# create association deletion json
def delete_association(student_suid,parent_suid):

    # needs to be this specific format per Schoology API docs
    # school_uid NOT uid
    association = {
        'associations':  {
            'association': {
                "student_school_uid" : student_suid,
                "parent_school_uid": parent_suid,
                "delete": 1
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
        s_email = student['primary_email'].lower()
        #print(s_email)
        s_suid = student['school_uid']
        student_dict.update({s_email:s_suid})

    return student_dict


# get parent dict from Schoology with email as key and school_uid as value
def get_parents():
    # build parent dictionary; need school_uid for parent association json
    parents = get_users(role_id=817463) # parent role id: 817463
    parents_dict = {}
    for parent in parents:
        p_email = parent['primary_email'].lower()
        p_suid = parent['school_uid']
        parents_dict.update({p_email:p_suid})

    return parents_dict


# get association from PS export, return list of dicts of unique parents that
# can be used to build new users jsons
def get_PSParents():
    emails = []
    data = []

    # open PowerSchool export; build parent info dicts
    with open(EXPORT, newline='', encoding="ISO-8859-1") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parent = {
                'LC_email': row['U_DEF_EXT_STUDENTS.contact1_email'].lower(),
                'first_name': row['U_DEF_EXT_STUDENTS.contact1_fname'],
                'last_name': row['U_DEF_EXT_STUDENTS.contact1_lname']
            }
            data.append(parent)
            emails.append(row['U_DEF_EXT_STUDENTS.contact1_email'].lower())

    # get unique parents to account for multi child families
    unique_emails = set(emails)

    # filter parent info for unique parents and append to list that is returned
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


# Builds associations {student_email,parent_email} from PowerSchool export
def get_PSassociation():
    # open and read PS export
    with open(EXPORT, newline='', encoding="ISO-8859-1") as csvfile:
        reader = csv.DictReader(csvfile)

        PS_association = {}
        for row in reader:
            student_email = row['U_DEF_EXT_STUDENTS.student_email'].lower()
            parent_email = row['U_DEF_EXT_STUDENTS.contact1_email'].lower()
            # append key:value pair to PS_association for return
            PS_association[student_email] = parent_email

    return PS_association


# get inactive parents from Schoology
def delete_inactiveParents():
    parent_jsons = get_PSParents()
    PS_emails = []
    for parent in parent_jsons:
        PS_emails.append(parent['LC_email'])

    # check for schoology parent accounts that have been deleted in PowerSchool
    schoology_parents = get_parents()
    for parent in schoology_parents:
        if(parent not in PS_emails):
            id = get_userID(parent)
            d = delete_user(id)


# update all PowerSchool associations in schoology
def associate():
    time.sleep(1)
    users = get_users()

    with open(EXPORT, newline='', encoding="ISO-8859-1") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            p_email = row['U_DEF_EXT_STUDENTS.contact1_email'].lower()
            s_email = row['U_DEF_EXT_STUDENTS.student_email'].lower()
            s_suid = get_userSUID(s_email,users)
            p_suid = get_userSUID(p_email,users)
            ass = create_parentAssociation(build_association(student_suid=s_suid,parent_suid=p_suid))
            fields = ass['association']
            code = fields[0]
            if(int(code['response_code']) == 400):
                d = {s_email: p_email}
                failed.append(d)
            time.sleep(1)

    message = "FALED SCHOOLOGY ASSOCIATIONS\n\nstudent_email,parent_email\n"
    for f in failed:
        s = str(f).replace("{","").replace("}","")
        s = s + "\n"
        message = message + s

    # send failed log email to admin
    mailer = pymail()
    mailer.create_message("******@******","FALED SCHOOLOGY ASSOCIATIONS",message)
    mailer.send_message()

    
# one time call to create an association according to student and parent email
def manual_association(student_email,parent_email):
    users = get_users()

    s_suid = get_userSUID(student_email,users)
    p_suid = get_userSUID(parent_email,users)
    print(create_parentAssociation(delete_association(student_suid=s_suid,parent_suid=p_suid)))


# Get new parents and update parent associations in Schoology
def main():

    # get {parent_email, school_uid} dictionary from Schoology
    schoology_parents = get_parents()

    # get parent jsons used to build schoology users
    parent_jsons = get_PSParents()

    # get parents with no accounts in Schoology and build new user json list
    new_parents = []
    for parent in parent_jsons:
        if( parent['LC_email'] not in schoology_parents):
            p = build_parent(parent['LC_email'],parent['first_name'],parent['last_name'])
            new_parents.append(p)

    for parent in new_parents:
        create_user(parent)
        time.sleep(1)

    # update all association
    associate()
    
    # remove PS export 
    if os.path.exists(EXPORT):
        os.remove(EXPORT)
    else:
        print("The file does not exist")


def test():
    pass


if __name__ == '__main__':
    main()
