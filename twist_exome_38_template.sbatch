#! /bin/bash
#SBATCH -A ngi2016001
#SBATCH -J TwistExome_=PROJECT=
#SBATCH -p core
#SBATCH -N 1
#SBATCH -n 4
#SBATCH -t 2-00:00:00
#SBATCH -o "/proj/ngi2016001/nobackup/NGI/ANALYSIS/=PROJECT=/TwistExome.%j.out"
#SBATCH -e "/proj/ngi2016001/nobackup/NGI/ANALYSIS/=PROJECT=/TwistExome.%j.err"
#SBATCH -D "/proj/ngi2016001/nobackup/NGI/ANALYSIS/=PROJECT=/"
#SBATCH --mail-user medsci-molmed-bioinfo@googlegroups.com
#SBATCH --mail-type TIME_LIMIT_80

PROJDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS/=PROJECT="
TARGETDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS/resources/target_files_wes"
OUTDIR="${PROJDIR}"
VERSIONPATH="/vulpes/ngi/=PATHENV=/=VERSION="

REFTSV="${PROJDIR}/reference_tsv"
SAMPLEFILE="${REFTSV}/=PROJECT=.tsv"
EXITCODE=${OUTDIR}/"TwistExome.exit_code"
RUNDEBUG=${OUTDIR}/"TwistExome.run_parameters"

TARGETPARAM="--target_bed ${TARGETDIR}/Twist_Exome_RefSeq_targets_hg38_100bp_padding.bed"
GENOMESPARAM="--genome GRCh38"
PROFILE="-profile uppmax"
SAREKTAG="$(sed -nre 's/^sarek: (.*)$/\1/p' "${VERSIONPATH}/resources/deployed_tools.upps.version")"

date '+%Y-%m-%d %R:%S' |tee ${RUNDEBUG}
cat "${0}" >> ${RUNDEBUG}
echo "" > ${EXITCODE}

source "${VERSIONPATH}/conf/sourceme_upps.sh"
source activate NGI

nextflow run \
  "${VERSIONPATH}/sw/sarek/workflow/" \
    "${PROFILE}" \
    --project ngi2016001 \
    -c "${VERSIONPATH}/conf/nextflow_miarka_upps.config" \
    -c "${VERSIONPATH}/conf/sarek_miarka.config" \
    -resume \
    --tag "${SAREKTAG}" \
    "${GENOMESPARAM}" \
    --input "${SAMPLEFILE}" \
    --outDir "${OUTDIR}" \
    --tools haplotypecaller,snpeff \
    --no_gatk_spark \
    "${TARGETPARAM}" \
    --generate_gvcf

echo "$?" > ${EXITCODE}
date '+%Y-%m-%d %R:%S' |tee -a ${RUNDEBUG}

