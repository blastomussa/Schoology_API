#!/usr/bin/env python3
# Author: Blastomussa
# Date 9/3/2021
# Class based implementation of Gmail API; for sending simple emails
# Requires credentials.json from Google Project in same directory
from __future__ import print_function
import base64
import os.path
from email.mime.text import MIMEText
from httplib2.error import ServerNotFoundError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class pymail:
    def __init__(self):
        self.SCOPES = ['https://mail.google.com/']
        self.authorize()


    def authorize(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)


    def create_message(self,to,subject,message_text):
        emailMsg = message_text
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = to
        mimeMessage['subject'] = subject
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        self.raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()


    def send_message(self):
        try:
            message = (self.service.users().messages().send(userId="me", body={'raw': self.raw_string}).execute())
            print('Message Id: %s' % message['id'])
            return message
        except(ServerNotFoundError,HttpError) as error:
            print('An error occurred: %s' % error)

# TEST EMAIL
mailer = pymail()
mailer.create_message("recipient@gmail.com","TEST","TEST")
mailer.send_message()
