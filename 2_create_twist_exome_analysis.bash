#!/bin/bash

SCRIPTSDIR="$(dirname "$(readlink -f "$0")")"
TEMPLATE="${SCRIPTSDIR}/twist_exome_38_template.sbatch"
ANALYSISDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS"

PROJECT=$1
VERSIONPATH="${2:-/vulpes/ngi/production/latest}"

if [[ -z "${PROJECT}" ]]
then
  echo
  echo "   This script requires at least one parameter, project:"
  echo "     $>bash 2_create_twist_exome_analysis.bash <project>"
  echo " ex: bash 2_create_twist_exome_analysis.bash AB-1234"
  echo
  echo "   If needed, a second parameter can be used two specify the path to the deployed environment (default is /vulpes/ngi/production/latest)"
  echo "     $>bash 2_create_twist_exome_analysis.bash <project> <environment>"
  echo " ex: bash 2_create_twist_exome_analysis.bash AB-1234 /vulpes/ngi/production/v22.05"
  echo
  exit 1
fi

PATHENV="$(basename "$(dirname "$(readlink -f "${VERSIONPATH}")")")"
VERSION="$(basename "$(readlink -f "${VERSIONPATH}")")"
SAREKTAG="$(sed -nre 's/^sarek: (.*)$/\1/p' "${VERSIONPATH}/resources/deployed_tools.upps.version")"

echo "${PROJECT} ${PATHENV} ${VERSION} ${SAREKTAG}"

PROJDIR="${ANALYSISDIR}/${PROJECT}"

mkdir -p "${PROJDIR}/logs"
mkdir -p "${PROJDIR}/scripts"

SCRIPTFILE="${PROJDIR}/scripts/twistexome.sbatch"

#  generate corresponding sbatch file using
sed \
  -e "s#=PROJDIR=#${PROJDIR}#g" \
  -e "s/=PROJECT=/${PROJECT}/g" \
  -e "s/=PATHENV=/${PATHENV}/g" \
  -e "s/=VERSION=/${VERSION}/g" \
  -e "s/=SAREKTAG=/${SAREKTAG}/g" \
  "${TEMPLATE}" > "${SCRIPTFILE}"

echo
echo "  check that the batch file looks ok and start the analysis by running"
echo "    $>sbatch ${SCRIPTFILE}"
echo

