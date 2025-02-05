#! /bin/bash -l

#SBATCH -A ngi2016001
#SBATCH -n 4
#SBATCH -N 1
#SBATCH -p core
#SBATCH -J hs_metrics
#SBATCH -t 6:00:00
#SBATCH -o hs_metrics.%j.out

#
# Run CollectHsMtrics for all markduplicate BAM/CRAM files in an analysis folder
#

BAITS=$1
TARGETS=$2
ANALYSISDIR=$3
INFILE=$4
METRICS=$5

# Genome reference needed for CRAM files
REF="/sw/data/uppnex/ToolBox/hg38bundle/Homo_sapiens_assembly38.fasta"

# singularity container for GATK version used by Sarek3.4.2, provides CollectHsMetrics
CONTAINER="/vulpes/ngi/containers/biocontainers/singularity-gatk4-4.5.0.0--py36hdfd78af_0.img"

#
# NOTE: This script is re-used for submitting sbatch jobs, in which case 5 parameters will be used. Users 
#       should only input 3 parameters though
#

if [[ $# -eq 3 ]]
then
  
  # This is the functionality when the user runs the script with 3 parameters. BAM/CRAM files will be located
  # and sbatch jobs for collecting metrics dispatched

  find "${ANALYSISDIR}/results/preprocessing/markduplicates/" -path "*/*.bam" -o -path "*/*.cram" | while read -r ALIGNMENTFILE
  do
    ALIGNMENTDIR="$(dirname "${ALIGNMENTFILE}")"
    ALIGNMENTNAME="$(basename "${ALIGNMENTFILE}")"

    # construct the path for the metrics file
    HSDIR="${ALIGNMENTDIR/preprocessing/reports}"
    HSDIR="${HSDIR/markduplicates/HsMetrics}"
    EXTENSION="${ALIGNMENTNAME##*.}"
    HSFILE="${ALIGNMENTNAME%.${EXTENSION}}.hs_metrics"

    mkdir -p "$HSDIR"
    sbatch -J "${HSFILE}" -o "${HSDIR}/${HSFILE}.out" "$0" "$BAITS" "$TARGETS" "$ANALYSISDIR" "$ALIGNMENTFILE" "${HSDIR}/${HSFILE}"
  done

elif [[ $# -eq 5 ]]
then

  # This is the functionality when the script is run as a sbatch job and launched with 5 parameters

  singularity exec $CONTAINER gatk --java-options -Xmx28g CollectHsMetrics \
    --INPUT $INFILE \
    --OUTPUT $METRICS \
    --MAX_RECORDS_IN_RAM 50000000 \
    --BAIT_INTERVALS $BAITS \
    --TARGET_INTERVALS $TARGETS \
    --REFERENCE_SEQUENCE $REF

else
  echo
  echo "     Run CollectHsMtrics for all recalibrated BAM files in an analysis folder"
  echo
  echo "     Usage:"
  echo 
  echo "       $> $(basename $0) <bait intervals> <target intervals> <analysis path>"
  echo
  echo "     The script will locate recalibrated BAM-files under <analysis path> and run CollectHsMetrics on each BAM file"
  echo "     using <bait intervals> and <target intervals>"
  echo 
  echo "     Output logs and metrics will be written under <analysis path>/results/Reports/<sample>/HsMetrics/"
  echo
fi
