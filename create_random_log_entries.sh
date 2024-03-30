#!/bin/bash

bulk_max_count=350

read -r -p $'Enter number of bulk log entries \033[0;36m(default: 100/max: 350)\033[0m: ' bulk_count
bulk_count=${bulk_count:-100}
(( bulk_count > bulk_max_count )) && bulk_count=bulk_max_count

read -r -p $'Enter cURL iterations \033[0;33m(default: 10)\033[0m: ' iteration
iteration=${iteration:-10}

for ((i=1; i<=iteration; i++))
do
  response=$(curl -X POST -d "bulk_count=$bulk_count" http://0.0.0.0:8000/create/create-bulk-auto 2>/dev/null)
    if [ $? -eq 0 ]; then
      if [[ -n "$response" ]]; then
        echo "$i: $bulk_count log entries created (Success)"
      else
        echo "$i: $bulk_count log entries failed to be created! (Possible Server-Side Error)"
      fi
    else
      echo "$i: $bulk_count log entries failed to be created! (cURL Error) "
    fi
done

total_entries=$((iteration * bulk_count))
final_text="$total_entries log entries have been processed"
text_length=${#final_text}
divider=$(printf '%*s' "$text_length" | tr ' ' '-')

echo "$divider"
echo "$final_text"
echo "$divider"
