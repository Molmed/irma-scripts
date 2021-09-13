#!/bin/bash
module load bioinfo-tools picard
java -jar /lupus/sw/bioinfo/picard/2.10.3/milou/picard.jar BedToIntervalList \
      I=/proj/ngi2016001/private/local_scripts/exome_scripts/Twist_Exome_RefSeq_targets_hg19.bed \
      O=/proj/ngi2016001/private/local_scripts/exome_scripts/Twist_Exome_RefSeq_targets_hg19.interval_list \
      SD=/sw/data/uppnex/ToolBox/ReferenceAssemblies/hg38make/bundle/2.8/b37/human_g1k_v37_decoy.dict
