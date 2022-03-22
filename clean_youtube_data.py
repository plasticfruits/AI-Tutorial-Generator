#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

col_dtype = {
    "id": str,
    "categoryId": "Int64",
    "categoryName": str,
    "categoryName": str,
    "title": str,
    "description": str,
    "publish_date": str,
}

# read CSV
raw_data = pd.read_csv(
    "./temp/01_youtube_video_data.csv",
    dtype=col_dtype,
    parse_dates=["publish_date"],
    index_col=0,
)
raw_data.info()

# Plot barchart
fig, ax = plt.subplots(figsize=(5, 4))
sns.histplot(data=raw_data, y="categoryName", stat="percent", edgecolor=None)
ax.set_title("Categories")
fig

# check for specific categories
raw_data.query("categoryName == 'Comedy'")


# clean
drop_cats = ["Music", "Gaming", "Pets & Animals", "Comedy"]
data = raw_data[raw_data.categoryName.isin(drop_cats) == False]

# Export
data = data.loc[:, ["id", "title"]]
data.to_csv("youtube_ids_clean.csv")
