# %%
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

#QUERY = input("Enter YouTube search query: ")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SECRET = "./credentials/credentials_franc.json"  # update with your credentials file here
#search_results = 5

query_df = pd.read_csv('temp/filter_queries.csv')
youtube_category_map = pd.read_csv("./tools/youtube_categoryId.csv")

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
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds)

def search(youtube, **kwargs):
    return youtube.search().list(part="snippet", **kwargs).execute()

def parse_youtube_response(response):
    """
    parameters: 
    output:
    """
    video_list = []
    items = response.get("items")
    for i in items:
        # if i['id']['kind'] == 'youtube#channel':
        #     pass
        # else:
        #     continue
        try:
            id = i["id"].get("videoId", "")
            title = i["snippet"]["title"]
            description = i["snippet"]["description"]
            publish_date = i["snippet"]["publishTime"]
        except:
            pass
        # create dictionary
        video_data = {
            "id": id,
            "title": title,
            "description": description,
            "publish_date": publish_date,
        }
        video_list.append(video_data)  # append to list
        #print(f"Fetching video: {title}")
    return video_list

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def get_video_categories(list_of_video_ids):
    """
    """
    dict_of_cats = []
    ids = [video['id'] for video in list_of_video_ids]
    for group in chunker(ids, 25):
        ids_str = ','.join(group)
        request = youtube.videos().list(
                part="snippet",
                id=ids_str)
        response = request.execute()
    # get categories for each video id
    
        for i in response['items']:
            dict = {}
            dict['id'] = i['id']
            dict['categoryId'] = i['snippet']['categoryId']
            dict_of_cats.append(dict)
    
    video_categories = pd.DataFrame.from_dict(dict_of_cats)
    video_categories['id'] = video_categories['id'].astype(str)
    video_categories['categoryId'] = video_categories['categoryId'].astype(int)
    return video_categories

    

#%%
# --------------
# MAIN PART
# --------------

# authenticate to YouTube API
youtube = youtube_authenticate()

# import search queries
query_df = pd.read_csv('filter_queries.csv')
query_df['Source'] = query_df['Source'].apply(lambda x: x.lower())
query_df = query_df.query("Source == 'youtube'")
youtube_queries = query_df['Query'].apply(lambda x: "how to " + x.lower()).to_list()

# %%
# --- 1. get list of all videos
youtube_videos = []
max_results = 500
for query in youtube_queries:
    video_list = []
    print(f"--- Fetching results for query: '{query}' ---")
    first_response = search(youtube, q=query, maxResults=max_results)
    next_page = first_response.get('nextPageToken', "") 
    video_list.extend(parse_youtube_response(first_response))
    while len(video_list) < max_results:
        response = search(youtube, 
                        q=query, 
                        maxResults=max_results, 
                        pageToken=next_page)
        try: 
            next_page = response["nextPageToken"]
            video_list.extend(parse_youtube_response(response))
        except:
            print("--- No more pages ---")
            video_list.extend(parse_youtube_response(response))
    youtube_videos.extend(video_list)
    print(f"--- {len(video_list)} URL's fetched ---")

# already_parsed_links = youtube_videos
# temp_export = pd.DataFrame(already_parsed_links)
# temp_export.to_csv("./temp/05_video_data.csv")

# %%
# --- 2. Get Categories of all videos

# Get categories of videos
video_categories = get_video_categories(youtube_videos)
video_categories = video_categories.merge(youtube_category_map, on='categoryId', how='left')

# get info of videos
video_df = pd.DataFrame(youtube_videos)
#video_df = video_df.loc[video_df["id"].isin(videos_with_subtitles), :]
video_df["publish_date"] = pd.to_datetime(video_df["publish_date"]).dt.date
video_df = video_categories.merge(video_df, on='id', how='left')
# export video meta-data as .csv
video_df.to_csv("youtube_video_data.csv")
print(f".csv file exported")
print(f"{video_df.shape[0]} total files created")



# %%
# --- 3. Get text of videos

# # Iterate over video-id's and create .txt files
# videos_with_subtitles = []
# for i in video_list:
#     video_script = "Solution: "  # initialise empty string
#     id = i["id"]
#     name = i["title"]
#     try:
#         video_transcript = YouTubeTranscriptApi.get_transcript(
#             video_id=id, languages=["en"]
#         )
#         print(f"Saving file as: {name}.txt")
#         videos_with_subtitles.append(id)
#         for j in video_transcript:
#             text = j["text"] + " "
#             video_script = video_script + text
#         with open(f"./scripts/youtube/{name}.txt", "w") as text_file:
#             print(video_script, file=text_file)
#     except:
#         print("-- Error: No subtitles available --")
#         pass



# # create df and filter by videos with subtitles available
# video_df = pd.DataFrame(video_list)
# video_df = video_df.loc[video_df["id"].isin(videos_with_subtitles), :]
# video_df["publish_date"] = pd.to_datetime(video_df["publish_date"]).dt.date

# # export video meta-data as .csv
# video_df.to_csv("video_data.csv")
# print(f".csv file exported")
# print(f"{video_df.shape[0]} total files created")


# %%
