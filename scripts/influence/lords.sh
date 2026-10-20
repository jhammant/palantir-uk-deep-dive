#!/bin/bash
cd "$1"
for s in $(seq 0 20 1300); do curl -s -A "palantir-uk-open-data/1.0" "https://members-api.parliament.uk/api/Members/Search?House=2&IsCurrentMember=true&skip=$s&take=20" | jq -r '.items[].value.id'; done | sort -u > ids.txt
wc -l ids.txt
while read id; do curl -s -A "palantir-uk-open-data/1.0" "https://members-api.parliament.uk/api/Members/$id/RegisteredInterests" -o int-$id.json; done < ids.txt
grep -l -i palantir int-*.json > hits.txt
wc -l hits.txt
