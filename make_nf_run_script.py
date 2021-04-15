import os
import argparse

parser = argparse.ArgumentParser(description='Generate run script for nextflow pipelines')
parser.add_argument('--project', required=True, help='Project name')
parser.add_argument('--genome', required=True, help='Reference genome, e.g. GRCm38')
parser.add_argument('--pipeline', required=True, choices=["rnaseq", "methylseq"], help='Analysis pipeline, e.g. methylseq')
parser.add_argument('--base-path', default=os.path.join("/proj", "ngi2016001", "nobackup", "NGI"), help='Path to the folder containing the ANALYSIS and DATA subfolders (default: %(default)s)')

args = parser.parse_args()
project = args.project
genome = args.genome
pipeline = args.pipeline
base_path = args.base_path

analysis_path = os.path.join(base_path, "ANALYSIS")
data_path = os.path.join(base_path, "DATA")
project_path = os.path.join(analysis_path, project)
scripts_path = os.path.join(project_path, "scripts")
logs_path = os.path.join(project_path, "logs")
self_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(self_path, "run_script_templates")
config_path = os.path.join(self_path, "config", "genomes_GRCh38_gencode.config")
extra_args = ""

# Create log and scripts folder (if not already created)
for d in [scripts_path, logs_path]:
  os.system(f"mkdir -p {d}")

# Handle gencode for GRCh38
if pipeline == 'rnaseq' and genome == 'GRCh38':
  extra_args = "--gencode"

# Copy template to scripts folder
os.system(f"cp {template_path}/{pipeline}_template {scripts_path}/run_analysis.sh")

# Add project and genome to template
sed_cmd = "sed -i"
for srch, rplc in [
  ("_PROJECT_", project),
  ("_GENOME_", genome),
  ("_ANALYSISDIR_", analysis_path),
  ("_DATADIR_", data_path),
  ("_CONFIG_", f"-c {config_path}"),
  ("_EXTRAARGS_", f"{extra_args}")]:
  sed_cmd = f"{sed_cmd} -e 's#{srch}#{rplc}#g'"

os.system(f"{sed_cmd} {scripts_path}/run_analysis.sh")

print(f"{scripts_path}/run_analysis.sh has been generated. Good luck with the analysis!")
