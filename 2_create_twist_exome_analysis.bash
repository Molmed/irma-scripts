#!/bin/bash

SCRIPTSDIR="$(dirname "$(readlink -f "$0")")"
ANALYSISDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS/"

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
sed "s/=PROJECT=/${project}/g" ${SCRIPTSDIR}/twist_exome_38_template.sbatch > ${ANALYSISDIR}${project}/twistexome.sbatch

#   check that the batch file looks ok and
#   start the analysis by running
#    $>  sbatch ${ANALYSISDIR}${project}/twistexome.sbatch
#
