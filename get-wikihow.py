# %%
import pandas as pd
from pywikihow import WikiHow

#QUERY = "fire !kindle !amazon"
#max_results = 15

# import query df
queries_df = pd.read_csv('temp/filter_queries.csv', index_col=False)
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
        article_name = "How to " + how_to['title'] # "Task: "
        steps = how_to['steps']
        body = '' # "Solution: "
        for step in steps:
            body = body + step['summary'] + "\n" + step['description'] + "\n"
        with open(f"./exports/wikihow/{article_name}.txt", "w") as text_file:
            print(body, file=text_file)
        count += 1
    query_count -= 1
    print(f"{count} articles fetched, {query_count} queries remaining.")
    
    
# %%
# # fetch summary content form WikiHow
# for i in WikiHow.search(QUERY, max_results=max_results):
#     how_to = i.as_dict()
#     article_name = how_to['title']
#     print(f"Fetching How To: {article_name} (summary)")
#     steps = how_to['steps']
#     body = 'Solution: '
#     for step in steps:
#         body = body + step['summary'] + "\n"
#     with open(f"./scripts/wikihow_summary/{article_name}.txt", "w") as text_file:
#         print(body, file=text_file)
