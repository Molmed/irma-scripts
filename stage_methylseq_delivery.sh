#!/bin/bash

# A helper script to stage deliveries for NF-core methylseq BP analysis results

set -e

PROJECT=$1

#Check if project given else print usage
if [ "$#" -ne 1 ]
then
  echo "Usage: stage_methylseq_delivery.sh <PROJECT_NAME>"
  exit 1
fi

STAGING_ROOT='/proj/ngi2016001/nobackup/NGI/DELIVERY'
ANALYSIS_ROOT='/proj/ngi2016001/nobackup/NGI/ANALYSIS'
STAGING_DIR="${STAGING_ROOT}/${PROJECT}"
ANALYSIS_DIR="${ANALYSIS_ROOT}/${PROJECT}"

README_LOCATION='/proj/ngi2016001/nobackup/private/workspace_sarek/README/'
README_NAME='METHYLSEQ_README.md'

#The location of the multiqc report in ANALYSIS_DIR, copied to seqsummaries 
REPORT_REL_LOCATION='results/MultiQC'
SEQSUM_ROOT='/proj/ngi2016001/incoming/reports'
SEQSUM_DIR="${SEQSUM_ROOT}/${PROJECT}"

echo "Staging $ANALYSIS_DIR into $STAGING_DIR"

# Tar qualimap-files and remove directory or delivery fails
cd "${ANALYSIS_DIR}/results"
tar cvzf qualimap.tar.gz ./qualimap

#Remove qualimap folder
rm -r ./qualimap

# Create staging directory
mkdir "${STAGING_DIR}"
cd "${STAGING_DIR}"

# Link result files
ln -s "${ANALYSIS_DIR}/results" .

#Copy readme (sample_correlation included? check file structure.) Add comment on dirs that may be omitted?
cp "${README_LOCATION}/${README_NAME}" .

# Calculate checksums
echo sbatch -A ngi2016001 -n 8 -t 10:00:00 -J "checksums_$PROJECT" -o "${ANALYSIS_DIR}/logs/checksums.log" -e "${ANALYSIS_DIR}/logs/checksums.log" --wrap "find results/ -type f -exec md5sum {} >> checksums.md5 \;"
sbatch -A ngi2016001 -n 8 -t 10:00:00 -J "checksums_$PROJECT" -o "${ANALYSIS_DIR}/logs/checksums.log" -e "${ANALYSIS_DIR}/logs/checksums.log" --wrap "find results/ -type f -exec md5sum {} >> checksums.md5 \;"

# Copy multiqc report to seqsummaries
mkdir -p "${SEQSUM_DIR}"
cp -r  "${ANALYSIS_DIR}/${REPORT_REL_LOCATION}/*" "${SEQSUM_DIR}"

