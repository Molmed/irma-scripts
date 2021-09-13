#!/bin/bash
# This script will make a reference tsv for a specific project in /proj/ngi2016001/nobackup/NGI/DATA/<project>
# Will create tsv file for sarek in /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>/reference_tsv


if [[ $# -eq 1 ]] ; then
  project=$1
else
  echo
  echo "     This script requires the parameter <project>, run as"
  echo "     $> 1_create_reference_tsv.bash <project>"
  echo
  exit 0
fi

echo "     Project: ${project}"

if [ ! -d "/proj/ngi2016001/nobackup/NGI/DATA/${project}" ]; then
  echo "/proj/ngi2016001/nobackup/NGI/DATA/${project} does not exist, will exit."
  exit 0
fi
echo "Will create tsv file for sarek in /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv."

mkdir -p /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv
find /proj/ngi2016001/nobackup/NGI/DATA/${project} | grep "_R[1,2]_001" | sort > /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv/temp.txt

python /proj/ngi2016001/private/local_scripts/exome_scripts/create_reference_tsv.py /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv/temp.txt /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv/${project}.tsv

## remove tmp file
rm /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv/temp.txt

echo "Inspect /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/reference_tsv/${project}.tsv and correct any errors detected."
