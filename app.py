
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import Flask, request, url_for, redirect, jsonify
from pprint import pprint
app = Flask(__name__)


@app.route('/darragh-talent', methods=['POST'])
def darragh_talent():
    data = json.dumps(request.form)
    data_dict = json.loads(data)
    command = data_dict['text'].split(' ', 1)[0]
    talent = ''
    resp = {}
    if command == 'add':
        talent = data_dict['text'].split(' ', 1)[1]
        resp = {"text": '{0} added!'.format(talent), "response_type": "in_channel"} if write_cells(
            talent) else 'Talent not added'
    elif command == 'get':
        cells = get_cells()
        resp = {"response_type": "in_channel",
                "text": '\n'.join(''.join(cell) for cell in cells)}
    return jsonify(resp), 200


def google_login():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_cells():
    creds = google_login()
    service = build('sheets', 'v4', credentials=creds)

    result = service.spreadsheets().values().get(
        spreadsheetId='17vUemXXb_XubiIEZkWlrjy7Ovmpt5t24SxwNDqpPglc', range='Sheet1').execute()

    numRows = result.get('values') if result.get('values')is not None else 0

    print('{0} rows retrieved.'.format(numRows))

    return numRows


def write_cells(data):
    creds = google_login()
    service = build('sheets', 'v4', credentials=creds)
    values = [[data]]
    body = {'values': values}

    result = service.spreadsheets().values().append(spreadsheetId='17vUemXXb_XubiIEZkWlrjy7Ovmpt5t24SxwNDqpPglc', range='Sheet1', valueInputOption='USER_ENTERED',
                                                    body=body).execute()

    print('{0} cells appended.'.format(
        result.get('updates').get('updatedCells')))
    return True


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
