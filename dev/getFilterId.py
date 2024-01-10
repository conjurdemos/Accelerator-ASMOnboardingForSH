#!/usr/local/bin/python3
import json
with open('sh-filters.json', 'r') as file:
    data = file.read()
filters_dict = json.loads(data)

safeName = "JodyDemo"
safeFilter = lambda x: ((x['type'] == 'PAM_SAFE') & (x['data']['safeName'] == safeName))
foundSource = [a for a in filters_dict['filters'] if safeFilter(a)]
if len(foundSource) == 0:
  print("Not found.")
elif len(foundSource) > 1:
  print("More than one found.")
else:
  sstore_id = foundSource.pop()['id']
  print(sstore_id)

