#!/usr/local/bin/python3
import json
with open('sh-stores.json', 'r') as file:
    data = file.read()
stores_dict = json.loads(data)

isSource = lambda x: 'SECRETS_SOURCE' in x['behaviors']
foundSource = [a for a in stores_dict['secretStores'] if isSource(a)]
if len(foundSource) == 0:
  print("Not found.")
elif len(foundSource) > 1:
  print("More than one found.")
else:
  sstore_id = foundSource.pop()['id']
  print(sstore_id)

