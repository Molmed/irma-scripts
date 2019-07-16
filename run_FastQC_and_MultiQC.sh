#!/bin/bash -l
# Author: Matilda Åslin (matilda.aslin@medsci.uu.se) & Monika Brandt (monika.brandt@medsci.uu.se)

if [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
  echo "" 
  echo "This script will create a MultiQC-report for all fastq files in a given directory."
  echo "It will search the directory given as input for fastq-files and then run FastQC on these file."
  echo "MultiQC will be started automatically after FastQC is done."
  echo ""
  echo "Arguments and options:" 
  echo "-h Display this text"
  echo "-p Path to the Project directory in Unaligned, i.e. /<absolute path to runfolder>/Unaligned/<project>/. Required."
  echo "-i INDEX If used, index-files will be included in the MultiQC report. Needed for chromium runs."
  echo "-u INTEGER or several INTEGERs separated by comma. Lane numbers to be  included in report for Undetermined indices."
  echo "   Will only work if fastq-files containing undetermined indices are located in Unaligned and if -p is pointing to /Unaligned/<project>/."
  echo ""
  echo "Example usage:"
  echo ""
  echo "bash run_FastQC_and_MultiQC.sh -p /full/path/to/runfolder/Unaligned/MyProject/ -i INDEX -u 2,4,6"
  echo ""
  exit 0
fi

while getopts p:i:u: option
do
case "${option}"
in

p) PROJECT_PATH=${OPTARG};;

i) INCLUDE_INDEX=${OPTARG};;

u) UNDET_LANES=${OPTARG};;

esac
done

if [ -z $PROJECT_PATH ]
then
  echo "ERROR: Project path have to specified"
  echo "Usage: run_FastQC_and_multiQC.sh /path/to/project/folder"
  exit
fi

if [ "$INCLUDE_INDEX" == "INDEX" ]
then
  echo "Will include index FASTQs in report"
  SEARCH_PATTERN='*fastq.gz'
else
  echo "Will NOT include index FASTQs in report"
  SEARCH_PATTERN='*_R[1-2]_*fastq.gz'
fi

PROJECT=`basename $PROJECT_PATH`

module load bioinfo-tools FastQC

# Get unique string
UNIQSTR=$(echo `date '+%Y%m%d%H%M%S'`$PROJECT)

sbatch -A ngi2016001 -p core -n 16 -t 02-00:00:00 -J FastQC_$PROJECT -e $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" -o $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" \
--wrap "mkdir $SNIC_TMP/$UNIQSTR; find $PROJECT_PATH -name \"$SEARCH_PATTERN\" | xargs -n 1 -P 16 -I{} fastqc -o $SNIC_TMP/$UNIQSTR {}; multiqc --template default --title $PROJECT -z $SNIC_TMP/$UNIQSTR -o $PROJECT_PATH"

sleep 5

# Get new unique string
UNIQSTR=$(echo `date '+%Y%m%d%H%M%S'`$PROJECT)

if [ $UNDET_LANES ] && [ "$INCLUDE_INDEX" == "INDEX" ]
then
  echo "A report will be created for undetermined indices from the following lanes: $UNDET_LANES"
  UNDET_PATH=`dirname $PROJECT_PATH`
  SEARCH_PATTERN='Undetermined_*_L00['{$UNDET_LANES}']_*fastq.gz'
  PROJECT=`basename $PROJECT_PATH`"_Undetermined"
  sbatch -A ngi2016001 -p core -n 16 -t 02-00:00:00 -J FastQC_$PROJECT -e $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" -o $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" \
  --wrap "mkdir $SNIC_TMP/$UNIQSTR; find $UNDET_PATH -name \"$SEARCH_PATTERN\" | xargs -n 1 -P 16 -I{} fastqc -o $SNIC_TMP/$UNIQSTR {}; multiqc --template default --title $PROJECT -z $SNIC_TMP/$UNIQSTR -o $PROJECT_PATH"
fi

if [ $UNDET_LANES ] && [ -z $INCLUDE_INDEX ]
then
  echo "A report will be created for undetermined indices from the following lanes: $UNDET_LANES"
  UNDET_PATH=`dirname $PROJECT_PATH`
  SEARCH_PATTERN='Undetermined_*_L00['{$UNDET_LANES}']_R[1-2]_*fastq.gz'
  PROJECT=`basename $PROJECT_PATH`"_Undetermined"
  sbatch -A ngi2016001 -p core -n 16 -t 02-00:00:00 -J FastQC_$PROJECT -e $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" -o $PROJECT_PATH"/fastqc_and_multiqc_"$PROJECT".log" \
  --wrap "mkdir $SNIC_TMP/$UNIQSTR; find $UNDET_PATH -name \"$SEARCH_PATTERN\" | xargs -n 1 -P 16 -I{} fastqc -o $SNIC_TMP/$UNIQSTR {}; multiqc --template default --title $PROJECT -z $SNIC_TMP/$UNIQSTR -o $PROJECT_PATH"
fi

