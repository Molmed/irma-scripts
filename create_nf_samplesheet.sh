#! /bin/bash

PROJ="$1"
ANALYSISPATH="$2"
DATAPATH="$3"
ENVPATH="$4"
PIPELINE="$5"

if [[ $# -ne 5 ]]
then
  echo
  echo "     This script requires the parameters <project name> <analysis path> <data path> <environment path> <pipeline>"
  echo
  echo "       example:"
  echo "         $ create_nf_samplesheet.sh \\"
  echo "             AB-1234 \\"
  echo "             /proj/ngi2016001/nobackup/NGI/ANALYSIS \\"
  echo "             /proj/ngi2016001/nobackup/NGI/DATA \\"
  echo "             /vulpes/ngi/production/latest \\"
  echo "             rnaseq"
  echo
  exit 1
fi

PROJDIR="$ANALYSISPATH/$PROJ"
DATADIR="$DATAPATH/$PROJ"

FQDIR="${PROJDIR}/fastqs"
mkdir -p ${FQDIR}

find "${DATADIR}" -name "*.fastq.gz" -exec ln -s {} "${FQDIR}/" \;


if [[ $PIPELINE == "rnaseq" || $PIPELINE == "methylseq" ]]
then
  python "$(find "$ENVPATH/sw/rnaseq" -name "fastq_dir_to_samplesheet.py" -print -quit)" \
    --sanitise_name \
    --sanitise_name_index=1 \
    --strandedness=reverse \
    "${FQDIR}" \
    "${PROJDIR}/${PROJ}.SampleSheet.csv"
elif [[ $PIPELINE == "sarek" ]]
then
  python create_sarek_samplesheet.py \
    ${FQDIR}" \
    "${PROJDIR}/${PROJ}.SampleSheet.csv"
else
  echo "Pipeline ${PIPELINE} not supported."
  exit 1      
fi