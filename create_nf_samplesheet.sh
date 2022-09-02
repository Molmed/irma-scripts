#! /bin/bash

PROJ="$1"
ANALYSISPATH="$2"
DATAPATH="$3"
ENVPATH="$4"

PROJDIR="$ANALYSISPATH/$PROJ"
DATADIR="$DATAPATH/$PROJ"

FQDIR="${PROJDIR}/fastqs"
mkdir -p ${FQDIR}

find "${DATADIR}" -name "*.fastq.gz" -exec ln -s {} "${FQDIR}/" \;

python "$ENVPATH/sw/rnaseq/workflow/bin/fastq_dir_to_samplesheet.py" \
  --sanitise_name \
  --sanitise_name_index=1 \
  --strandedness=reverse \
  "${FQDIR}" \
  "${PROJDIR}/${PROJ}.SampleSheet.csv"
