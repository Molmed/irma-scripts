#! /bin/bash

PROJ="$1"
ANALYSISPATH="$2"
DATAPATH="$3"
PIPELINE="$4"

if [[ $# -ne 4 ]]
then
  echo
  echo "     This script requires the parameters <project name> <analysis path> <data path> <pipeline>"
  echo
  echo "       example:"
  echo "         $ create_nf_samplesheet.sh \\"
  echo "             AB-1234 \\"
  echo "             /proj/ngi2016001/nobackup/NGI/ANALYSIS \\"
  echo "             /proj/ngi2016001/nobackup/NGI/DATA \\"
  echo "             rnaseq"
  echo
  exit 1
fi

PROJDIR="$ANALYSISPATH/$PROJ"
DATADIR="$DATAPATH/$PROJ"
SCRIPT_DIR=$(dirname $(realpath "$0"))

if [[ $PIPELINE == "rnaseq" || $PIPELINE == "methylseq" ]]
then
  python "${SCRIPT_DIR}/fastq_dir_to_samplesheet.py" \
    --sanitise_name \
    --sanitise_name_index=1 \
    --strandedness=reverse \
    "${DATADIR}" \
    "${PROJDIR}/${PROJ}.SampleSheet.csv"
elif [[ $PIPELINE == "sarek" ]]
then
  python "${SCRIPT_DIR}/create_sarek_samplesheet.py" \
    "${DATADIR}" \
    "${PROJDIR}/${PROJ}.SampleSheet.csv"
else
  echo "Pipeline ${PIPELINE} not supported."
  exit 1      
fi
