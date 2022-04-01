#!/bin/bash
# This script will make a reference tsv for a specific project in /proj/ngi2016001/nobackup/NGI/DATA/<project>
# Will create tsv file for sarek in /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>/reference_tsv

DATADIR="/proj/ngi2016001/nobackup/NGI/DATA/"
ANALYSISDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS/"

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

if [ ! -d "${DATADIR}${project}" ]; then
  echo "${DATADIR}${project} does not exist, will exit."
  exit 0
fi
echo "Will create tsv file for sarek in ${ANALYSISDIR}${project}/reference_tsv."

mkdir -p ${ANALYSISDIR}${project}/reference_tsv
find ${DATADIR}${project} -name "*_R[1,2]_001*" | sort > ${ANALYSISDIR}${project}/reference_tsv/temp.txt

create_reference_tsv.py ${ANALYSISDIR}${project}/reference_tsv/temp.txt ${ANALYSISDIR}${project}/reference_tsv/${project}.tsv

## remove tmp file
rm ${ANALYSISDIR}${project}/reference_tsv/temp.txt

echo "Inspect ${ANALYSISDIR}${project}/reference_tsv/${project}.tsv and correct any errors detected."
