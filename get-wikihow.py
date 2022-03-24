# %%
import pandas as pd
from pywikihow import WikiHow
import json 

#QUERY = "fire !kindle !amazon"
#max_results = 15

# import query df
queries_df = pd.read_csv('temp/filter_queries_1.csv', index_col=False)
queries_df = queries_df.query("Source == 'WikiHow'")
queries_df.info()

# create lsit of queries
wikihow_queries = queries_df.Query.to_list()

# %%
# fetch extended content

query_count = len(wikihow_queries)
for query in wikihow_queries:
    print(f"Fetching results for query: '{query}'")
    count = 1
    for i in WikiHow.search(query, max_results=100):
        how_to = i.as_dict()
        title = "How to " + how_to.get('title')
        steps = how_to['steps']
        body = ''
        for step in steps:
            body = body + step['description'] + "\n"
        short = ''
        for step in steps:
            short = short + step['summary'] + "\n"
        dict = {'task': title, 'solution': body, 'summary': short}
        with open(f"./exports/wikihow/{title}.json", "w") as out_file:
            json.dump(dict, out_file, indent = 3)  
        count += 1
    query_count -= 1
    print(f"{count} articles fetched, {query_count} queries remaining.")
    



