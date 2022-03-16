# %%
from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter

video_id = 'ZPr-a8kht2E'
video_title = 'How to Start a Fire in a Survival Situation | Basic Instincts | WIRED'
video_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

# formatter = TextFormatter()
# text_formatted = formatter.format_transcript(video_transcript)

# %% 
# Extract text
video_text = ''
for i in video_transcript:
    text = i['text']+' '
    video_script = video_script + text    
    
# save to text file
with open(f"./scripts/{video_title}.txt", "w") as text_file:
    print(video_script, file=text_file)

# %%

