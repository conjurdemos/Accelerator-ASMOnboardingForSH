#!/usr/local/bin/python3
import json
with open('sh-policies.json', 'r') as file:
    data = file.read()
policies_dict = json.loads(data)

sstore_id = "store-aeaa2dd3-7d99-47aa-9989-49f56f9f987f"
filter_id = "filter-301340a1-8af0-4da4-b938-1034639038aa"
tstore_id = "store-9303f8b4-9031-4bb6-bfd6-9817ba0fbf3a"


isPolicy = lambda x: ((x['state']['current'] == 'ENABLED')
			& (x['source']['id'] == sstore_id)
			& (x['target']['id'] == tstore_id)
			& (x['filter']['id'] == filter_id)
)
foundPolicy = [a for a in policies_dict['policies'] if isPolicy(a)]
if len(foundPolicy) == 0:
  print("Not found.")
elif len(foundPolicy) > 1:
  print("More than one found.")
else:
  policy_id = foundPolicy.pop()['id']
  print(policy_id)

