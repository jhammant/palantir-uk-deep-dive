#!/bin/bash
cd "$1"
while read id; do [ -s dl/parl/pqid/$id.json ] || { curl -s -A "palantir-uk-open-data/1.0" "https://questions-statements-api.parliament.uk/api/writtenquestions/questions/$id?expandMember=true" -o dl/parl/pqid/$id.json; sleep 0.25; }; done < out/all-pq-ids.txt
while read id; do [ -s dl/parl/debates/$id.json ] || { curl -s -A "palantir-uk-open-data/1.0" "https://hansard-api.parliament.uk/debates/debate/$id.json" -o dl/parl/debates/$id.json; sleep 0.25; }; done < out/all-debate-ids.txt
curl -s -A "palantir-uk-open-data/1.0" "https://questions-statements-api.parliament.uk/api/writtenstatements/statements/1671624" -o dl/parl/hcws57.json
ls dl/parl/pqid | wc -l; ls dl/parl/debates | wc -l
