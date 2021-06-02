import sys
import os

project = sys.argv[1]

os.system("mkdir -p /proj/ngi2016001/nobackup/NGI/DATA/merged_fastqs_{}".format(project))

logs_path = "/proj/ngi2016001/nobackup/NGI/ANALYSIS/{}/logs".format(project)

os.system("mkdir -p {}".format(logs_path))

os.system('sbatch -A ngi2016001 -p core -n 8 -t 3-00:00:00 -J merge_fastqs_{1} -o {0}/merge_fastqs.log -e {0}/merge_fastqs.log --wrap "python /lupus/ngi/production/latest/sw/upps_standalone_scripts/merge_fastqs.py --input_dir /proj/ngi2016001/nobackup/NGI/DATA/{1} --output_dir /proj/ngi2016001/nobackup/NGI/DATA/merged_fastqs_{1}"'.format(logs_path, project))

