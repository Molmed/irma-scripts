# irma-scripts
Stand-alone scripts deployed to Miarka

These scripts are deployed to `/vulpes/ngi/production/latest/sw/upps_standalone_scripts/` by the miarka-provision process.
The script directory is added to PATH when loading the Miarka environment, meaning that these scripts are available on the command-line. 

The scripts should contain instructions for usage unless it's obvious how to use them. Preferably, invoking a script 
without arguments should be safe to run without any side effects and only display usage instructions on stdout

__NEVER__ put any passwords, usernames, tokens, user data or other sensitive information in the scripts. If such
information is required by the script, rely on reading it from an environment variable instead. 

When adding a new script to this repository, be sure to add a brief description of its purpose below:

* __concordance_check.sh__ - bash script to perform concordance check between a vcf file with genotypes and a vcf file 
with variant calls
* __deliver_project_to_user.sh__ - bash wrapper script around the deliver.py script, which should facilitate the 
delivery for the SNP platform
* __find_unorganized_flowcells.sh__ - bash script that verifies that the organized project folder under the DATA 
directory contains all runfolders in incoming having data from the project in them
* __link_project_sisyphus_reports.sh__ - bash script that links sisyphus runfolder reports from the incoming folder to
the corresponding project folder under ANALYSIS
* __set_charon_genotyping_status.sh__ - bash script to set the genotyping status field in charon to a specified value 
for samples present in a supplied vcf file
* __statdump_to_json.pl__ - perl script that can parse a statdump zipfile created by sisyphus and output the statistics
as json
* __run_FastQC_and_MultiQC.sh__ - bash script to run FastQC on a specified project in a runfolder. 
The script will summarize the output in one or several MultiQC-reports.
* __run_multiqc_bp_qc.sh__ - A simple wrapper for the MultiQC command used when performing QC of best-practice WGS projects.
* __project_runfolders.sh__ - Mainly used to find all runfolders with samplesheets containing a specific project or sample name.
Scans incoming for csv-files at most two folders down and greps for the given string, then echoes folder if found.
* __cleanup_nf_projects.py__ - Script for cleaning up old analysis nextflow projects. The script will list folders (with full path)
 that will be deleted and calculate how much data will be removed. It will wait for input from user before removing anything. See usage at the top of the script.
* __make_nf_run_script.py__ - Script for generating an sbatch run script for NextFlow rnaseq and methylseq pipelines. See usage at the top of the script.
* __merge_fastqs.py__ - Script for merging fastq-files from different lanes / runs per sample.
* __start_merge.py__ - Convenience script for merging fastq files in a project per sample, depends on merge_fastqs.py
* __1_create_reference_tsv.bash__ - A helper script to create_reference_tsv.py. 
* __create_reference_tsv.py__ - A script for writing sample info and paths to a WES project's fastq-files in a .tsv-file used by Sarek.
* __2_create_twist_exome_analysis.bash__ - This script will use a template, twist_exome_38_template.sbatch, to create a sbatch script to start Sarek for WES analysis.
* __twist_exome_38_template.sbatch__ - Template for running Sarek 2.6.1 on WES-data using reference GRCh38.
* __charon_project_samples_status_update.sh__ - Script to get all samples in Charon for a supplied project and set the analysis_status to ANALYZED and the status to STALE.
* __run_hs_metrics.sh__ - Run CollectHsMtrics for all recalibrated BAM files in a WES project.
* __bed2interval_list.sh__ - Example script on how to run picard BedToIntervalList (format needed for run_hs_metrics.sh).
