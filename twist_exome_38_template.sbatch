#! /bin/bash
#SBATCH -A ngi2016001
#SBATCH -J TwistExome_=PROJECT=
#SBATCH -p core
#SBATCH -N 1
#SBATCH -n 4
#SBATCH -t 2-00:00:00
#SBATCH -o "=PROJDIR=/logs/twistexome.%j.out"
#SBATCH -e "=PROJDIR=/logs/twistexome.%j.err"
#SBATCH -D "=PROJDIR="
#SBATCH --mail-user medsci-molmed-bioinfo@googlegroups.com
#SBATCH --mail-type TIME_LIMIT_80

PROJDIR="=PROJDIR="
TARGETDIR="${PROJDIR}/../resources/target_files_wes/human_comprehensive_exome"
OUTDIR="${PROJDIR}/results"
VERSIONPATH="/vulpes/ngi/=PATHENV=/=VERSION="

REFTSV="${PROJDIR}/reference_tsv"
SAMPLEFILE="${REFTSV}/=PROJECT=.SarekGermlineAnalysis.tsv"
EXITCODE="${PROJDIR}/twistexome.exit_code"
RUNDEBUG="${PROJDIR}/logs/twistexome.run_parameters"

TARGETPARAM="--target_bed ${TARGETDIR}/Twist_Comprehensive_Exome_Covered_Targets_hg38_100bp_padding.bed"
GENOMESPARAM="--genome GRCh38"
PROFILE="-profile uppmax"
SAREKTAG="=SAREKTAG="

date '+%Y-%m-%d %R:%S' |tee "${RUNDEBUG}"
cat "${0}" >> "${RUNDEBUG}"
echo "" > "${EXITCODE}"

source "${VERSIONPATH}/conf/sourceme_upps.sh"
source activate NGI

nextflow run \
  "${VERSIONPATH}/sw/sarek/workflow/" \
    "${PROFILE}" \
    --project ngi2016001 \
    -c "${VERSIONPATH}/conf/nextflow_miarka_upps.config" \
    -c "${VERSIONPATH}/conf/sarek_upps.config" \
    -resume \
    --tag "${SAREKTAG}" \
    "${GENOMESPARAM}" \
    --input "${SAMPLEFILE}" \
    --outdir "${OUTDIR}" \
    --tools haplotypecaller,snpeff \
    "${TARGETPARAM}" \
    --generate_gvcf

echo "$?" > "${EXITCODE}"
date '+%Y-%m-%d %R:%S' |tee -a "${RUNDEBUG}"
