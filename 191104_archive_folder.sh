#! /bin/bash -l

FOLDER=$1

if [[ "$(readlink -f $(dirname $FOLDER))" != "$(readlink -f $(pwd))" ]]
then
  echo "Make sure that you are running the script from the folder containing $(basename $FOLDER)"
  exit 1
fi

FOLDER="$(basename $FOLDER)"

if [[ ! -e "$FOLDER" ]]
then
  echo "$FOLDER does not exist"
  exit 1
fi

echo " **** $FOLDER **** "

# create an archive folder with symlinks
echo "$(date) - curl -s -X POST -d '{\"remove\": \"False\"}' localhost:20489/api/1.0/create_dir/$FOLDER"
resp=$(curl -s -X POST -d '{"remove": "False"}' localhost:20489/api/1.0/create_dir/$FOLDER)
echo "$resp"

# calculate checksums
echo "$(date) - curl -s -X POST localhost:20489/api/1.0/gen_checksums/${FOLDER}_archive"
resp="$(curl -s -X POST localhost:20489/api/1.0/gen_checksums/${FOLDER}_archive)"
echo "$resp"
id=$(echo "$resp" |jq '.job_id')
state=$(echo "$resp" |jq '.state')
while [[ "$state" != "\"done\"" ]]
do
  sleep 30
  resp="$(curl -s localhost:20489/api/1.0/status/$id)"
  state=$(echo "$resp" |jq '.state')
  echo "$(date) - curl -s localhost:20489/api/1.0/status/$id - $state"
  if [[ "$state" == "\"error\"" ]]
  then
    echo "$(date) - encountered error - exiting"
    echo "Failed archiving $FOLDER"
    echo " **** $FOLDER **** "
    exit 1
  fi
done

# upload to archive
echo "$(date) - curl -s -X POST localhost:20489/api/1.0/upload/${FOLDER}_archive"
resp="$(curl -s -X POST localhost:20489/api/1.0/upload/${FOLDER}_archive)"
echo "$resp"
id=$(echo "$resp" |jq '.job_id')
state=$(echo "$resp" |jq '.state')
while [[ "$state" != "\"done\"" ]]
do
  sleep 60
  resp="$(curl -s localhost:20489/api/1.0/status/$id)"
  state=$(echo "$resp" |jq '.state')
  echo "$(date) - curl -s localhost:20489/api/1.0/status/$id - $state"
  if [[ "$state" == "\"error\"" ]]
  then
    echo "$(date) - encountered error - exiting"
    echo "Failed archiving $FOLDER"
    echo " **** $FOLDER **** "
    exit 1
  fi
done

echo "Successfully archived $FOLDER"
echo " **** $FOLDER **** "
