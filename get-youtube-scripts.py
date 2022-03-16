# %%
# import urllib.parse as p
import re
import os
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_transcript_api import YouTubeTranscriptApi

QUERY = input()
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SECRET = "/Users/alcachofa/Documents/Encrpyted/secrets/credentials.json"

# --------------
# FUNCTIONS
# --------------

def youtube_authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = SECRET
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds)
    
    
def search(youtube, **kwargs):
    return youtube.search().list(
        part="snippet",
        **kwargs
    ).execute()
    

# def get_video_details(youtube, **kwargs):
#     return youtube.videos().list(
#         part="snippet,contentDetails,statistics",
#         **kwargs
#     ).execute()

# %%
# --------------
# MAIN PART
# --------------

# authenticate to YouTube API
youtube = youtube_authenticate()

# perform search
response = search(youtube, q=QUERY, maxResults=3)
items = response.get("items")

# extract elements
video_list = []
for i in items:
    id = i["id"]["videoId"]
    title = i["snippet"]["title"]
    description = i["snippet"]["title"]
    publish_date = i["snippet"]["publishTime"]
    # create dictionary
    video_data = {'id': id, 
                  'title': title, 
                  'description': description,
                  'publish_date': publish_date
                  }
    video_list.append(video_data) # append to list
    print(f"fetching... {title}")
# %%

# Iterate over video-id's and create .txt files
video_script = ''
for i in video_list:
    id = i['id']
    print(f"saving .txt file... {id}")
    video_transcript = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
    for i in video_transcript:
        text = i['text']+' '
        video_script = video_script + text 
    with open(f"./scripts/{id}.txt", "w") as text_file:
        print(video_script, file=text_file)
