# TESTING
import pandas as pd
from pywikihow import WikiHow
import json 

query = 'Use Household Items to Remove Shoe Odors'
result = WikiHow.search(query, max_results=1)
how_to = result.as_dict()
print(how_to)

    
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