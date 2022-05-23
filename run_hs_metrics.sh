#! /bin/bash -l

#SBATCH -A ngi2016001
#SBATCH -n 4
#SBATCH -N 1
#SBATCH -p core
#SBATCH -J hs_metrics
#SBATCH -t 6:00:00
#SBATCH -o hs_metrics.%j.out

#
# Run CollectHsMtrics for all recalibrated BAM files in an analysis folder
#

BAITS=$1
TARGETS=$2
ANALYSISDIR=$3
INBAM=$4
METRICS=$5

# singularity container used by sarek, provides CollectHsMetrics
CONTAINER=/vulpes/ngi/containers/sarek/nfcore-sarek-2.7.img

#
# NOTE: This script is re-used for submitting sbatch jobs, in which case 5 parameters will be used. Users 
#       should only input 3 parameters though
#

if [[ $# -eq 3 ]]
then
  
  # This is the functionality when the user runs the script with 3 parameters. BAM files will be located
  # and sbatch jobs for collecting metrics dispatched

  find "${ANALYSISDIR}/results/Preprocessing" -path "*/Recalibrated/*.bam" |while read -r BAM
  do
    BAMDIR="$(dirname "${BAM}")"
    BAMNAME="$(basename "${BAM}")"

    # construct the path for the metrics file
    HSDIR="${BAMDIR/Preprocessing/Reports}"
    HSDIR="${HSDIR/Recalibrated/HsMetrics}"
    HSFILE="${BAMNAME/.bam/.hs_metrics}"

    mkdir -p "$HSDIR"
    sbatch -J "${HSFILE}" -o "${HSDIR}/${HSFILE}.out" "$0" "$BAITS" "$TARGETS" "$ANALYSISDIR" "$BAM" "${HSDIR}/${HSFILE}"
  done

elif [[ $# -eq 5 ]]
then

  # This is the functionality when the script is run as a sbatch job and launched with 5 parameters

  singularity exec $CONTAINER gatk --java-options -Xmx28g CollectHsMetrics --INPUT=$INBAM --OUTPUT=$METRICS --MAX_RECORDS_IN_RAM=50000000 --BAIT_INTERVALS=$BAITS --TARGET_INTERVALS=$TARGETS

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
