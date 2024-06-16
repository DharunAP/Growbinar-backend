from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ['zoom_client_id']
CLIENT_SECRET = os.environ['zoom_secret_id']
ACCOUNT_ID = os.environ['zoom_account_id']

def encode_client_credentials():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return encoded_credentials


def get_access_token_view():
    url = "https://zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encode_client_credentials()}"
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        return JsonResponse(response.json(), status=response.status_code)


def create_meeting_view(request):
    access_token = get_access_token_view()
    # access_token = "eyJzdiI6IjAwMDAwMSIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6ImUzMTdlMDQyLTA0ZWQtNGFjNC05YjU0LTZlZWU2ZTNjNjBiMyJ9.eyJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiI1bHZOYk1PWlQ2bVlaYUVIUGI5dVNnIiwidmVyIjo5LCJhdWlkIjoiNDYxZDYxNGQxZDRiOTNhNTA1MzY1NTU0ODYwZDBkMGMiLCJuYmYiOjE3MTgxMzQ4MzMsImNvZGUiOiIxNndiNHk0QlRwdUJIMGZVZV8yYmZBakVIR1g2ZG5MNkIiLCJpc3MiOiJ6bTpjaWQ6QlZYZ1NmNmpRYmlwMHhBSU9JcE9nIiwiZ25vIjowLCJleHAiOjE3MTgxMzg0MzMsInR5cGUiOjMsImlhdCI6MTcxODEzNDgzMywiYWlkIjoiQTNRX3FKMlhTMjY5ZTlKSUQ5SzNodyJ9.0SBcUoTE6pV8BugVfcxfZdUrUp1jd_tTvhkUTjzgws7JtZC6P_jbITYDO2AibzcBda6Oa5D8LscH97nIyoKQ3A"
    topic = 'Default Topic'
    start_time = request['start_time']
    duration = int(30)
    timezone = 'UTC'

    meeting_url = 'https://api.zoom.us/v2/users/me/meetings'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    meeting_data = {
        'topic': topic,
        'type': 2,  # Scheduled meeting
        'start_time': start_time,
        'duration': duration,
        'timezone': timezone
    }
    response = requests.post(meeting_url, headers=headers, json=meeting_data)
    if response.status_code == 201:
        return response.json()
    else:
        return None
