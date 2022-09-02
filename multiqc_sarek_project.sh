#!/bin/bash -l

# Script for making project level MultiQC reports for sarek
# Two reports are made: One for a bioinformatician to inspect QC and one to send to the user.
# Before the reports are generated, a MultiQC custom content config is generated to add a sample list section and
# pipeline info to the reports.
#
# This script will in turn submit two separate slurm jobs for generating the reports and then exit
#
# Usage:
#  - bash multiqc_sarek_project.sh /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>
#
# A custom script location can be supplied as a second argument (useful during testing):
#   - bash multiqc_sarek_project.sh /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project> /path/to/scripts_dir
#

PROJECT_PATH=$1
PROJECT_ID=$(basename $PROJECT_PATH)
REPORT_FILENAME=$PROJECT_ID"_multiqc_report"
REPORT_FILENAME_QC=$PROJECT_ID"_multiqc_report_qc"
REPORT_OUTDIR="${PROJECT_PATH}/results/multiqc_ngi"

if [ -z "$2" ]
  then
    SCRIPTS_DIR="/vulpes/ngi/production/latest/sw/upps_standalone_scripts"
  else
    SCRIPTS_DIR=$2
fi
CONFIG_DIR=$SCRIPTS_DIR"/config"

check_errors()
{
  # Parameter 1 is the return code
  # Parameter 2 is text to display on failure.
  if [ "${1}" -ne "0" ]; then
    echo "ERROR # ${1} : ${2}"
    exit ${1}
  fi
}

source activate NGI

# Generate custom content listing the samples in the project
python "$SCRIPTS_DIR/sample_list_for_multiqc.py" --path "${PROJECT_PATH}"
check_errors $? "Something went wrong when making the sample list"

mqc_content="$PROJECT_PATH/multiqc_custom_content"
mkdir -p "$mqc_content"
mv "$PROJECT_PATH/sample_list_mqc.yaml" "$mqc_content/"

# Generate custom content based on the pipeline_info output
infodir="$(find "$PROJECT_PATH" -mindepth 2 -maxdepth 4 -type d -name "pipeline_info" -a -path "*/results/*" -print -quit)"
if [ -e "${infodir}" ]
then
  python "$SCRIPTS_DIR/multiqc_pipeline_info.py" "$infodir" "$mqc_content"
fi

# Gather a list of input dirs to give to MultiQC, exclude report directories not placed directly under the main sample
# (i.e. reports for individual lanes etc. will be excluded)
sed -nre 's/^.*<li>([^<]+)<\/li>.*$/\1/p' "$mqc_content/sample_list_mqc.yaml" > "$mqc_content/sample_names.txt"
INPUT_DIRS="$mqc_content $(find "$PROJECT_PATH" -mindepth 3 -maxdepth 5 -type d -name "${PROJECT_ID}*" -a -path "*/Reports/*" |grep -f <(while read s; do echo "$s\$"; done < "$mqc_content/sample_names.txt") | paste -s -d' ')"

# submit MultiQC jobs to SLURM
SBATCH_A=ngi2016001
SBATCH_n=2
SBATCH_t=12:00:00
SBATCH_D="${REPORT_OUTDIR}"

mkdir -p "${REPORT_OUTDIR}"

SBATCH_J="${PROJECT_ID}_multiqc_qc"
sbatch -A ${SBATCH_A} -D "${SBATCH_D}" -n ${SBATCH_n} -t ${SBATCH_t} -J "${SBATCH_J}" -o "${SBATCH_J}.%j.out" --wrap "multiqc \
  -f \
  --template default \
  --config '$CONFIG_DIR/multiqc_config_wgs.yaml' \
  --config '$CONFIG_DIR/multiqc_config_wgs_qc.yaml' \
  --title '$PROJECT_ID' \
  --filename '$REPORT_FILENAME_QC' \
  --outdir '$REPORT_OUTDIR' \
  --data-format json \
  --zip-data-dir \
  --no-push \
  --interactive \
  $INPUT_DIRS"

SBATCH_J="${PROJECT_ID}_multiqc"
sbatch -A ${SBATCH_A} -D "${SBATCH_D}" -n ${SBATCH_n} -t ${SBATCH_t} -J "${SBATCH_J}" -o "${SBATCH_J}.%j.out" --wrap "multiqc \
  -f \
  --template default \
  --config '$CONFIG_DIR/multiqc_config_wgs.yaml' \
  --title '$PROJECT_ID' \
  --filename '$REPORT_FILENAME' \
  --outdir '$REPORT_OUTDIR' \
  --data-format json \
  --zip-data-dir \
  --no-push \
  $INPUT_DIRS"
