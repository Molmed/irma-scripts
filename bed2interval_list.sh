#!/bin/bash
module load bioinfo-tools picard
java -jar ${PICARD_HOME}/picard.jar BedToIntervalList \
      I=/PATH/TO/BED_INPUT/Twist_Exome_RefSeq_targets_hg19.bed \
      O=/PATH/TO/INTERVAL_LIST_OUTPUT/Twist_Exome_RefSeq_targets_hg19.interval_list \
      SD=/vulpes/common/data/uppnex/ToolBox/ReferenceAssemblies/hg38make/bundle/2.8/b37/human_g1k_v37_decoy.dict
