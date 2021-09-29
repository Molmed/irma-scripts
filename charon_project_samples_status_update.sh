#! /bin/bash -l

## 
## List all samples in Charon for a supplied project and set the analysis_status to ANALYZED and the status to STALE
##

PROJ=$1

if [[ -z $PROJ ]]
then
  echo "A project identifier must be specified"
  exit 1
fi

for SAMPLE in $(
curl \
-s \
-H "X-Charon-API-token:${CHARON_API_TOKEN}" \
-H "Content-Type:application/json" \
-X GET ${CHARON_BASE_URL}/api/v1/samples/$PROJ |python -m json.tool |sed -nre 's/.*"sampleid"[^"]+"([^"]+).*/\1/p'
)
do

  curl \
  -H "X-Charon-API-token:${CHARON_API_TOKEN}" \
  -H "Content-Type:application/json" \
  -X PUT \
  -d "{\"status\":\"STALE\"}" \
  ${CHARON_BASE_URL}/api/v1/sample/${PROJ}/${SAMPLE}

  curl \
  -H "X-Charon-API-token:${CHARON_API_TOKEN}" \
  -H "Content-Type:application/json" \
  -X PUT \
  -d "{\"analysis_status\":\"ANALYZED\"}" \
  ${CHARON_BASE_URL}/api/v1/sample/${PROJ}/${SAMPLE}

done
