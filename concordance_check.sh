#! /bin/sh

SAMPLE=$1
GTFILE=$2
GVCF=$3
POSITIONS=$4

if [[ -z "${GVCF}" ]]
then
  GVCF=../07_variant_calls/${SAMPLE}.clean.dedup.recal.bam.genomic.vcf.gz
fi

if [[ ! -z "${POSITIONS}" ]]
then
  POSITIONS="-L ${POSITIONS}"
fi

EVAL=${SAMPLE}.eval.vcf.gz

# First, re-call positions from the GVCF in order to produce HOM_REF calls
java -jar /sw/apps/bioinfo/GATK/3.3.0/GenomeAnalysisTK.jar \
-T GenotypeGVCFs \
-R /vulpes/common/data/uppnex/piper_references/2016-04-07/gatk_bundle/2.8/b37/human_g1k_v37.fasta \
--variant ${GVCF} \
--out ${EVAL} \
${POSITIONS} \
--includeNonVariantSites 

# Next, calculate the concordance between the calls and the genotypes
java -jar /sw/apps/bioinfo/GATK/3.3.0/GenomeAnalysisTK.jar \
-T GenotypeConcordance \
-R /vulpes/common/data/uppnex/piper_references/2016-04-07/gatk_bundle/2.8/b37/human_g1k_v37.fasta \
-eval ${EVAL} \
-comp ${GTFILE} \
-sites ${SAMPLE}.discordant_sites \
-o ${SAMPLE}.gt_concordance
