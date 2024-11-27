#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser(description='Generate run script for nextflow pipelines')
parser.add_argument('--project', required=True, help='Project name')
parser.add_argument('--genome', required=True, help='Reference genome, e.g. GRCm38')
parser.add_argument('--pipeline', required=True, choices=["rnaseq", "methylseq", "sarek"],
                    help='Analysis pipeline, e.g. methylseq')
parser.add_argument('--base-path', default=os.path.join("/proj", "ngi2016001", "nobackup", "NGI"),
                    help='Path to the folder containing the ANALYSIS and DATA subfolders '
                         '(default: %(default)s)')
parser.add_argument('--environment-path',
                    default=os.path.join("/vulpes", "ngi", "production", "latest"),
                    help='Path to the deployed environment (default: %(default)s)')
parser.add_argument('--em-seq', action='store_true', default=False,
                    help='Run Methylseq pipeline with --em-seq flag (default: %(default)s)')
parser.add_argument('--wes', action='store_true', default=False,
                    help='Run Sarek pipeline for WES analysis')

args = parser.parse_args()
project = args.project
genome = args.genome
pipeline = args.pipeline
base_path = args.base_path
environment_path = args.environment_path
em_seq = args.em_seq
wes = args.wes

analysis_path = os.path.join(base_path, "ANALYSIS")
data_path = os.path.join(base_path, "DATA")
project_path = os.path.join(analysis_path, project)
scripts_path = os.path.join(project_path, "scripts")
logs_path = os.path.join(project_path, "logs")
self_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(self_path, "run_script_templates")
config_path = os.path.join(self_path, "config", "genomes_GRCh38_gencode.config")
extra_args = ""

resolved_env_path = os.path.realpath(environment_path)

# Create log and scripts folder (if not already created)
for d in [scripts_path, logs_path]:
    os.system(f"mkdir -p {d}")

# Handle gencode for GRCh38
if pipeline == 'rnaseq' and genome == 'GRCh38':
    extra_args = "--gencode"
# Handle GRCh38 iGenome for sarek
if pipeline == 'sarek' and genome == 'GRCh38':
    genome = "GATK.GRCh38"
# Add EM-seq parameter
if pipeline == 'methylseq' and em_seq:
    extra_args = "--em_seq"

# Create a samplesheet
os.system(
    f"create_nf_samplesheet.sh {project} {analysis_path} {data_path} {resolved_env_path} {pipeline}")
if pipeline == 'methylseq':
    # Remove the last column (strandedness) from samplesheet
    samplesheet_file = os.path.join(
        project_path,
        f"{project}.SampleSheet.csv"
    )
    tmp_file = os.path.join(
        project_path,
        f".{project}.SampleSheet.csv.tmp"
    )
    os.system(
        f"cut -f1,2,3 -d, {samplesheet_file} > {tmp_file} && "
        f"mv {tmp_file} {samplesheet_file}"
    )

# Copy template to scripts folder
os.system(f"cp {template_path}/{pipeline}_template {scripts_path}/run_analysis.sh")

# Add project and genome to template
sed_cmd = "sed -i"
for srch, rplc in [
  ("_ENVPATH_", resolved_env_path),
  ("_PROJECT_", project),
  ("_GENOME_", genome),
  ("_ANALYSISDIR_", analysis_path),
  ("_DATADIR_", data_path),
  ("_CONFIG_", f"-c {config_path}"),
  ("_EXTRAARGS_", f"{extra_args}")]:
    sed_cmd = f"{sed_cmd} -e 's#{srch}#{rplc}#g'"

os.system(f"{sed_cmd} {scripts_path}/run_analysis.sh")

# Set up parameters for sarek run in a separate json file
# Could be implemented for rnaseq but not the methylseq version that we use
if pipeline == 'sarek':
    sed_cmd = "sed -i"
    os.system(f"cp {template_path}/{pipeline}_params_template {scripts_path}/params.json")
    if not wes:
        os.system(f"{sed_cmd} '/^wes/d;/^intervals/d' {scripts_path}/parameters.json")
    for srch, rplc in [
        ("_PROJECTPATH_", project_path),
        ("_PROJECT_", project),
        ("_GENOME_", genome)]:
        sed_cmd = f"{sed_cmd} -e 's#{srch}#{rplc}#g'"

os.system(f"{sed_cmd} {scripts_path}/params.json")



print(f"{scripts_path}/run_analysis.sh has been generated. Good luck with the analysis!")
