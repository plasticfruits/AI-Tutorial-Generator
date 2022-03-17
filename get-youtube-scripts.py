# %%
import re
import os
import pickle
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from youtube_transcript_api import YouTubeTranscriptApi

# --------------
# VARIABLES
# --------------

QUERY = input("Enter YouTube search query: ")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SECRET = "credentials.json" # update with your credentials file here
max_results = 100

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
    # if there are no (valid) credentials available, let the user log in.
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

#%%
# --------------
# MAIN PART
# --------------

# print results parameter
print(f"--- Note: maximum results set to {max_results} ---")

# authenticate to YouTube API
youtube = youtube_authenticate()

# perform search
response = search(youtube, q=QUERY, maxResults=max_results)
next_page = response['nextPageToken']
items = response.get("items")

# TODO: Add another parent loop to iterate over next_page token

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
    print(f"Fetching video: {title}")



# Iterate over video-id's and create .txt files
videos_with_subtitles = []
for i in video_list:
    video_script = '' # initialise empty string
    id = i['id']
    try:
        video_transcript = YouTubeTranscriptApi.get_transcript(video_id=id, languages=['en'])
        print(f"Saving subtitle file as {id}.txt")
        videos_with_subtitles.append(id)
        for j in video_transcript:
            text = j['text'] + ' '
            video_script = video_script + text 
        with open(f"./scripts/{id}.txt", "w") as text_file:
            print(video_script, file=text_file)
    except:
        print("-- Error: No subtitles available --")
        pass


# create df and filter by videos with subtitles available
video_df = pd.DataFrame(video_list)
video_df = video_df.loc[ video_df['id'].isin(videos_with_subtitles), : ]
video_df['publish_date'] = pd.to_datetime(video_df['publish_date']).dt.date

# export video meta-data as .csv
video_df.to_csv('video_data.csv')
print(f".csv file exported")
print(f"{video_df.shape[0]} total files created")

# %%
