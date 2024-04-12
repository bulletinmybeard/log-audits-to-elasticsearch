#!/bin/sh

NOW=$(date +"%Y%m%d%H%M")

# Grab the names of volumes that are mounted on `/usr/share/...`
BACKUP_VOLUMES=$(df -h | grep '/usr/share' | awk -F'/' '{print $(NF-1)}')

for volume in $BACKUP_VOLUMES
do
    echo "Backing up volume '$volume'."
    if tar -czvf "/backup/${volume}_data_${NOW}.tar.gz" "/usr/share/${volume}/data" >/dev/null 2>&1; then
        echo -e "Backup of $volume completed successfully.\n"
    else
        echo -e "Error: Backup of $volume failed.\n" >&2
    fi
done
