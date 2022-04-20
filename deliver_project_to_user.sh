#! /bin/bash -l

###
# This is a simple wrapper around the deliver.py script, which should facilitate the delivery for the SNP platform
###

# Expects project id, email address and "sensitive" or "not-sensitive" as arguments. Optionally, specify a ";"-delimited list of members email addresses
PROJECT=$1
EMAIL=$2
SENSITIVE="--$3"
MEMBERS="$4"

# display usage instructions when invoked without arguments
if [[ -z "$PROJECT" ]]
then
  echo ""
  echo "Deliver SNP genotyping data to SNIC users via GRUS"
  echo ""
  echo "    usage: ${0} <PROJECT ID> <PI EMAIL> {sensitive|not-sensitive} ['member_1@email.se;member_2@email.se']"
  echo ""
  exit 1
fi

# Add members
MEMBER_ARG=""
if [[ ! -z "$MEMBERS" ]]
then
  MEMBER_ARG="--member_email"
  for a in $(echo "$MEMBERS" |sed -re 's/;/ /g')
  do
    MEMBER_ARG="$MEMBER_ARG $a"
  done
fi

# set up paths
GENOTYPEDIR="/proj/ngi2016001/incoming/GENOTYPING"
STAGINGDIR="$GENOTYPEDIR/staging"
SUPRCREDS="$GENOTYPEDIR/supr_creds.txt"
PROJPATH="$GENOTYPEDIR/$PROJECT"
LOGFILE=${0}.log
OUTFILE=${0}.out
ERRFILE=${0}.err
TSTAMP=$(date +%s)
MD5FILE="$GENOTYPEDIR/${PROJECT}.${TSTAMP}.md5"
ORIGINAL_CWD="$(pwd)"

# make the genotypedir the cwd
cd "$GENOTYPEDIR"

# File containing the SUPR credentails
URL=$(cut -f 1 "$SUPRCREDS")
USR=$(cut -f 2 "$SUPRCREDS")
PASS=$(cut -f 3 "$SUPRCREDS")

# Command to launch the delivery script
CMD=$(echo /vulpes/ngi/production/latest/sw/anaconda/envs/ugc_delivery_script/bin/python \
/vulpes/ngi/production/latest/sw/ugc_delivery_src/deliver.py \
--supr_url $URL \
--supr_api_user $USR \
--supr_api_key $PASS \
--staging_area $STAGINGDIR \
--path $PROJPATH \
--project $PROJECT \
--email $EMAIL \
--path-to-mover /usr/local/bin \
$SENSITIVE $MEMBER_ARG)

# Calculate MD5 sums of all delivered files
find $PROJECT -type f -exec md5sum {} \; > $MD5FILE
mv $MD5FILE $PROJPATH/

# Log the delivery
MSG="$TSTAMP  "$(date -d @$TSTAMP --utc +"%Y-%m-%dT%H:%M:%SZ")"  $(hostname)  ${USER}  ${PROJPATH}/$(basename $MD5FILE)  "$(echo $CMD |sed -re "s/$PASS/**************/")
echo "$MSG" |tee -a $LOGFILE $OUTFILE $ERRFILE

# Execute the command, duplicating stdout and stderr to files
$CMD 1> >(tee -a $OUTFILE) 2> >(tee -a $ERRFILE >&2)

# change the cwd back
cd "$ORIGINAL_CWD"
