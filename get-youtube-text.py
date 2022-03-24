# %%
from os import kill
import json
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi

# --------------
# VARIABLES
# --------------

youtube_df = pd.read_csv('temp/youtube_ids_clean.csv', index_col=0)
youtube_df.shape
# --------------
# MAIN PART
# --------------

# %%
# --- 1. Get text of videos
count = youtube_df.shape[0]
for index, row in youtube_df.iterrows():
    print(f"File saved, {count} pending")
    count -= 1
    script = "" # script = "Solution: "
    video_id = row['id']
    video_title = row['title']
    try:
        video_transcript = YouTubeTranscriptApi.get_transcript(
            video_id=video_id, languages=["en"])
        for i in video_transcript:
            text = i["text"] + " "
            script = script + text
        dict = {'task': video_title, 'solution': script}
        with open(f"./exports/youtube/{video_title}.json", "w") as out_file:
            json.dump(dict, out_file, indent = 3)
    except:
        print("-- Error: No subtitles available --")
        pass

# %%
