#!/bin/bash

SCRIPTSDIR="/proj/ngi2016001/private/local_scripts/exome_scripts"

if [[ $# -eq 1 ]] ; then
  project=$1
else
  echo
  echo "   This script requires one parameter, project:"
  echo "     $>bash 2_create_twist_exome_analysis.bash <project>"
  echo " ex: bash 2_create_twist_exome_analysis.bash AB-1234"
  echo
  exit 0
fi

echo ${project}

#  generate corresponding sbatch file using
sed "s/=PROJECT=/${project}/g" ${SCRIPTSDIR}/twist_exome_38_template.sbatch > /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/twistexome.sbatch

#   check that the batch file looks ok and
#   start the analysis by running
#    $>  sbatch /proj/ngi2016001/nobackup/NGI/ANALYSIS/${project}/twistexome.sbatch
#
