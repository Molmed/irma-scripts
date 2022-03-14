#! /bin/bash -l

#SBATCH -A ngi2016001
#SBATCH -n 2
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

# output folder for metrics and logs 
OUTDIR="${ANALYSISDIR}/results/Reports/HsMetrics"

# singularity container used by sarek, provides CollectHsMetrics
CONTAINER=/vulpes/ngi/containers/sarek/nf-core-sarek-2.7.simg

#
# NOTE: This script is re-used for submitting sbatch jobs, in which case 5 parameters will be used. Users 
#       should only input 3 parameters though
#

if [[ $# -eq 3 ]]
then
  
  # This is the functionality when the user runs the script with 3 parameters. BAM files will be located
  # and sbatch jobs for collecting metrics dispatched

  mkdir -p "${OUTDIR}"
  for BAM in $(find "${ANALYSISDIR}/results/Preprocessing/"*"/Recalibrated" -name "*.bam")
  do
    BAMNAME=$(basename "$BAM")
    METRICS="$OUTDIR/${BAMNAME/.bam/.hs_metrics}"
    sbatch -J "$(basename $METRICS)" -o "${METRICS}.out" "$0" "$BAITS" "$TARGETS" "$ANALYSISDIR" "$BAM" "$METRICS"
  done

elif [[ $# -eq 5 ]]
then

  # This is the functionality when the script is run as a sbatch job and launched with 5 parameters

  singularity exec $CONTAINER gatk --java-options -Xmx30g CollectHsMetrics --INPUT=$INBAM --OUTPUT=$METRICS --MAX_RECORDS_IN_RAM=50000000 --BAIT_INTERVALS=$BAITS --TARGET_INTERVALS=$TARGETS

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
  echo "     Output logs and metrics will be written under <analysis path>/results/Reports/HsMetrics/" 
  echo
fi
