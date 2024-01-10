#!/bin/bash

main() {
#  dupFilter
#  dupTarget
  dupPolicy
}

##################################
dupFilter() {
  echo "Test adding duplicate filter..."

  sourceId="store-aeaa2dd3-7d99-47aa-9989-49f56f9f987f"
  safe="JodyDemo"

  echo "Before..."
  ./shub-cli.sh filters_get "$sourceId" | jq ".filters[] | select(.data.safeName == \"$safe\")"
  echo "Add duplicate filter..."
  newId=$(./shub-cli.sh filter_create $sourceId $safe | jq -r .id)
  echo "After..."
  ./shub-cli.sh filters_get "$sourceId" | jq ".filters[] | select(.data.safeName == \"$safe\")"
  echo "Deleting duplicate..."
  ./shub-cli.sh filter_delete "$sourceId" "$newId"
  echo "Duplicate deleted."
  ./shub-cli.sh filters_get "$sourceId" | jq ".filters[] | select(.data.safeName == \"$safe\")"
}

##################################
dupTarget() {
  echo "Test adding duplicate target store..."
  name="secrethub-demo - US West (N. California)"
  desc="Garnet Secrets Hub"
  type="AWS_ASM"
  alias="secrethub-demo"
  acct="475601244925"
  region="us-west-1"
  role="GarnetDemo-AllowSecretsAccessRole-8CM2FXHKYD9Y"
  ./shub-cli.sh store_target_create "$name" "$desc" "$type" "$alias" "$acct" "$region" "$role"
}

##################################
dupPolicy() {
  echo "Test adding duplicate policy..."

  name="JodyTest-ca-central-1"
  desc="Description missing in original"
  source="store-aeaa2dd3-7d99-47aa-9989-49f56f9f987f"
  target="store-344a8ac1-3b1e-4275-960d-76a5b75b08f9"
  filter="filter-301340a1-8af0-4da4-b938-1034639038aa"

  echo "Before..."
  ./shub-cli.sh policies_target_get "$target"
  echo "Adding duplicate policy..."
  newId=$(./shub-cli.sh policy_create "$name" "$desc" "$source" "$target" "$filter" | jq -r .id)
  echo "After..."
  ./shub-cli.sh policies_target_get "$target"
  echo "Disabling policy..."
  ./shub-cli.sh policy_state "$newId" "disable"
  echo "Deleting policy..."
  ./shub-cli.sh policy_delete "$newId"
  echo "Deleted policy."
  ./shub-cli.sh policies_target_get "$target"
}

main "$@"
