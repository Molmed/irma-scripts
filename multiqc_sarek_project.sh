#!/bin/bash -l

# Script for making project level MultiQC reports for sarek
# Two reports are made: One for a bioinformatician to inspect QC and one to send to the user.
# Before the reports are generated, a MultiQC custom content config is generated to add a sample list section to the reports.
#
# Usage:
#  - Locally: bash multiqc_sarek_project.sh /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>
#  - Submitted to compute node (RECOMMENDED): sbatch multiqc_sarek_project.sh /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project>
#
# A custom script location can be supplied as a second argument (useful during testing):
#   - bash multiqc_sarek_project.sh /proj/ngi2016001/nobackup/NGI/ANALYSIS/<project> /path/to/scripts_dir
#
#SBATCH -A ngi2016001
#SBATCH -n 8
#SBATCH -t 05:00:00
#SBATCH -J sarek_multiQC
#SBATCH -o multiqc_sarek_project.%j.out
PROJECT_PATH=$1
PROJECT_ID=$(basename $PROJECT_PATH)
REPORT_FILENAME=$PROJECT_ID"_multiqc_report"
REPORT_FILENAME_QC=$PROJECT_ID"_multiqc_report_qc"

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

python $SCRIPTS_DIR"/sample_list_for_multiqc.py" --path $PROJECT_PATH
check_errors $? "Something went wrong when making the sample list"

multiqc -f --template default --config $CONFIG_DIR"/multiqc_config_wgs.yaml" --config $CONFIG_DIR"/multiqc_config_wgs_qc.yaml" --title $PROJECT_ID --filename $REPORT_FILENAME_QC --outdir $PROJECT_PATH"/multiqc_ngi" --data-format json --zip-data-dir --no-push $PROJECT_PATH
check_errors $? "Something went wrong when making the report for QC"

multiqc -f --template default --config $CONFIG_DIR"/multiqc_config_wgs.yaml" --title $PROJECT_ID --filename $REPORT_FILENAME --outdir $PROJECT_PATH"/multiqc_ngi" --data-format json --zip-data-dir --no-push $PROJECT_PATH
check_errors $? "Something went wrong when making the user report"

