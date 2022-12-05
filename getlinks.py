from __future__ import print_function

import numpy as np
import pandas as pd

import os.path
from profanity_filter import ProfanityFilter

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly', 'https://www.googleapis.com/auth/classroom.announcements.readonly']


def main():
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds)

        # https://classroom.googleapis.com/v1/courses/{courseId}/announcements
        # service_a = build('classroom', )
        #course = service.courses().get(id=course_id).execute()

        # Call the Classroom API
        results = service.courses().list(pageSize=10000).execute()
        courses = results.get('courses', [])

        courseId = results['courses'][0]['id']

        announcements = service.courses().announcements().list(courseId=courseId).execute()

        samples = []

        features = ['courseName']

        for i in announcements['announcements'][0]:
            features.append(i)

        pf = ProfanityFilter()

        for i in range(len(courses)):
            courseId = results['courses'][i]['id']
            name = results['courses'][i]['name']
            announcements = service.courses().announcements().list(courseId=courseId).execute()
            # print("Announcements under", name)

            if(len(announcements)>=1):
                for j in range(len(announcements['announcements'])):
                    curr_sample = []
                    curr_sample.append(name)
                    for feature in range(1, len(features)):
                        if(features[feature]=='text'):
                            curr_sample.append(pf.censor(announcements['announcements'][j][features[feature]]))
                        else:
                            curr_sample.append(announcements['announcements'][j][features[feature]])
                    samples.append(curr_sample)
                  
        
        
        df = pd.DataFrame(samples, columns=features)
        df.to_csv('Data.csv', index=False)




        # if not courses:
        #     print('No courses found.')
        #     return
        # # Prints the names of the first 10 courses.
        # print('Courses:')
        # for course in courses:
        #     print(course['name'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()