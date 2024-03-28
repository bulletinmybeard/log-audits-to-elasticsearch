#!/bin/bash

read -r -p $'Enter number of bulk log entries \033[0;36m(default: 100/max: 350)\033[0m: ' bulk_count
bulk_count=${bulk_count:-100}

read -r -p $'Enter cURL iteration \033[0;33m(default: 10)\033[0m: ' iteration
iteration=${iteration:-10}

for ((i=1; i<=iteration; i++))
do
  curl --output /dev/null --silent --head -X POST -d "bulk_count=$bulk_count" http://127.0.0.1:8000/create/auto-bulk
  echo "$i: $bulk_count log entries created"
done

total_entries=$((iteration * bulk_count))
final_text="$total_entries log entries have been created"
text_length=${#final_text}

divider=$(printf '%*s' "$text_length" | tr ' ' '-')

echo "$divider"
echo "$final_text"
echo "$divider"
