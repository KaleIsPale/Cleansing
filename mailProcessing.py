from __future__ import print_function

import json
import base64
import os.path
import spamcheck as model

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

'''
Labels:
CHAT
SENT
- INBOX (to be not removed)
IMPORTANT
TRASH 
DRAFT
CATEGORY_FORUMS
CATEGORY_UPDATES
CATEGORY_PERSONAL
CATEGORY_PROMOTIONS
CATEGORY_SOCIAL
STARRED
Subscribe
'''

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']
verified_adresses = []
with open('verified_addresses.txt', 'r') as wb:
    string = wb.read()
    list_ = string.split(',')
    verified_adresses = list_
    print(verified_adresses)


def filterMail(mail_list, service_api, progressVar, total_num_mail):
    tnum = total_num_mail
    var = progressVar
    spam = 0
    ham = 0
    num = 0
    for mail in mail_list:
        id = mail.get('id')
        requestBody_original = {
              "addLabelIds": [
                'INBOX'
              ],
              "removeLabelIds": [
                'SPAM',
              ]
        }
        requestBody_if_spam = {
              "addLabelIds": [
                'SPAM'
              ],
              "removeLabelIds": [
                'INBOX',
              ]
        }
        mail_message = service_api.users().messages().modify(id=id, userId='me', body=requestBody_original).execute()

        mail_message = service_api.users().messages().get(id=id, userId='me').execute()
        # mail_labels = mail_message.get('labelIds')
        mail_payload = mail_message.get('payload')
        headers = mail_payload.get('headers')
        for header in headers:
            if header.get('name') == 'From':
                address_full = header.get('value')
                if address_full[address_full.rfind('<')+1:address_full.rfind('>')] not in verified_adresses:
                    try:
                        body = base64.b64decode(mail_payload.get('body').get('data') + '==').decode('ascii', errors='ignore')
                        result = model.check(email=body, report=True)
                        score = result['score']
                        if float(score) >= 7.43:
                            msg = service_api.users().messages().modify(id=id, userId='me', body=requestBody_if_spam)
                            print('spam')
                            spam += 1
                        else:
                            print('ham')
                            ham += 1
                    except Exception as e:
                        pass
                else:
                    continue
        num += 1
        percent = (num/tnum) * 100
        var.set(percent)
                
                # address = address_full[address_full.rfind('<')+1:address_full.rfind('>')]
                # print(address)
        # result = model.check()


def main(process=False, progressVar=None, progressBar=None):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    progressBar.pack()
    def process_mail():
        try:
            messages_list = []
            query = 'in:INBOX'
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', q=query, includeSpamTrash=True).execute()
            messages = results.get('messages')
            pageToken = results.get('nextPageToken')
            num = results.get('resultSizeEstimate')
            messages_list = messages_list + messages
            while pageToken:
                results = service.users().messages().list(userId='me', q=query, pageToken=pageToken).execute()
                messages = results.get('messages')
                messages_list = messages_list + messages
                num += results.get('resultSizeEstimate')
                if 'nextPageToken' in results.keys():
                    pageToken = results.get('nextPageToken')
                else:
                    break
            
            filterMail(mail_list=messages_list, service_api=service, progressVar=progressVar, total_num_mail=num)
        # with open('results.json', 'w') as wb:
            # json.dump(messages_list, fp=wb)
        except HttpError as error:
            print(f'An error occurred: {error}')
    if process:
        process_mail()

# if __name__ == '__main__':
#     main()