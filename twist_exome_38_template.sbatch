#! /bin/bash
#SBATCH -A ngi2016001
#SBATCH -J TwistExome_=PROJECT=
#SBATCH -p core
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 10-00:00:00
#SBATCH -o "/lupus/proj_nobackup/ngi2016001/NGI/ANALYSIS/=PROJECT=/TwistExome.%j.out"
#SBATCH -e "/lupus/proj_nobackup/ngi2016001/NGI/ANALYSIS/=PROJECT=/TwistExome.%j.err"
#SBATCH -D "/lupus/proj_nobackup/ngi2016001/NGI/ANALYSIS/=PROJECT=/"
#SBATCH --mail-user medsci-molmed-bioinfo@googlegroups.com
#SBATCH --mail-type TIME_LIMIT_80
TARGETDIR="/proj/ngi2016001/nobackup/NGI/ANALYSIS/resources/target_files_wes/"
REFTSV="/lupus/proj_nobackup/ngi2016001/NGI/ANALYSIS/=PROJECT=/reference_tsv/"
SAMPLEFILE="${REFTSV}=PROJECT=.tsv"
OUTDIR="/lupus/proj_nobackup/ngi2016001/NGI/ANALYSIS/=PROJECT=/"
VERSIONPATH="/lupus/ngi/production/v1.25/"
TARGETPARAM="--targetBED ${TARGETDIR}Twist_Exome_RefSeq_targets_hg38_100bp_padding.bed"
GENOMEPARAM="--genome GRCh38"
EXITCODE=${OUTDIR}"TwistExome.exit_code"
PROFILE="-profile uppmax"
TAG="--tag 2.6.1"

date '+%Y-%m-%d %R:%S' > ${EXITCODE}
date '+%Y-%m-%d %R:%S'
cat ${OUTDIR}"twistexome.sbatch" >> ${EXITCODE}
echo ""

source ${VERSIONPATH}conf/sourceme_upps.sh
source activate NGI

nextflow run ${VERSIONPATH}sw/sarek/workflow/ ${PROFILE} --project ngi2016001 -c ${VERSIONPATH}conf/nextflow_irma_upps.config -c ${VERSIONPATH}conf/sarek_irma.config --custom_config_base ${VERSIONPATH}sw/sarek/configs/ --igenomes_ignore -resume ${TAG} ${GENOMESPARAM} --input ${SAMPLEFILE} --outDir ${OUTDIR} --tools haplotypecaller,snpeff --no_gatk_spark ${TARGETPARAM}


echo "$?" >> ${EXITCODE}
date '+%Y-%m-%d %R:%S' >> ${EXITCODE}
date '+%Y-%m-%d %R:%S'

