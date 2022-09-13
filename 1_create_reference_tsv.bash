#!/bin/bash
# This script will make a reference tsv for a specific project in /proj/ngi2016001/nobackup/NGI/DATA/<project>
# Will create tsv file for sarek in /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>/reference_tsv

NGIDIR="/proj/ngi2016001/nobackup/NGI"
DATADIR="${NGIDIR}/DATA"
ANALYSISDIR="${NGIDIR}/ANALYSIS"

if [[ $# -eq 1 ]]
then
  project=$1
else
  echo
  echo "     This script requires the parameter <project>, run as"
  echo "     $> 1_create_reference_tsv.bash <project>"
  echo
  exit 1
fi

echo "     Project: ${project}"

if [ ! -d "${DATADIR}/${project}" ]
then
  echo "${DATADIR}/${project} does not exist, will exit."
  exit 1
fi

OUTDIR="${ANALYSISDIR}/${project}/reference_tsv"
OUTFILE="${project}.SarekGermlineAnalysis.tsv"
echo "Will create ${OUTFILE} for sarek in ${OUTDIR}"

mkdir -p "${OUTDIR}"
find "${DATADIR}/${project}" -name "*_R[1,2]_001*" | sort > "${OUTDIR}/temp.txt"

create_reference_tsv.py "${OUTDIR}/temp.txt" "${OUTDIR}/${OUTFILE}"

## remove tmp file
rm "${OUTDIR}/temp.txt"

echo "Inspect ${OUTDIR}/${OUTFILE} and correct any errors detected."
