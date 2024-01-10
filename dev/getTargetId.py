#!/usr/local/bin/python3
import json
with open('sh-stores.json', 'r') as file:
    data = file.read()
stores_dict = json.loads(data)

account_id = "475601244925"
region_id = "us-east-1"

# filter out Source & non-AWS stores because they don't have entries for AWS account/region
isAwsTarget = lambda x: (
            (x["type"] == "AWS_ASM") & ("SECRETS_TARGET" in x["behaviors"])
        )
allTargets = [t for t in stores_dict["secretStores"] if isAwsTarget(t)]
isTheTarget = lambda x: (
            (x["data"]["accountId"] == account_id)
            & (x["data"]["regionId"] == region_id)
        )
foundTarget = [a for a in allTargets if isTheTarget(a)]
if len(foundTarget) == 0:
  print("Not found.")
elif len(foundTarget) > 1:
  print("More than one found.")
else:
  tstore = foundTarget.pop()
  print(tstore)
