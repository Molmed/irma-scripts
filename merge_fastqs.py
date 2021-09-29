from __future__ import print_function
import argparse
import re
import os
import shutil

arg_parser = argparse.ArgumentParser(description=""" Merges all fastq-files that match the standard name pattern per sample and read. Looks through the given dir and subdirs.""")
arg_parser.add_argument("--input_dir", metavar='Input directory', required=True, help="Base directory for the fastq files that should be merged. ")
arg_parser.add_argument("--output_dir", metavar='Output directory', required=True, help="Path for output of merged files.")
args = arg_parser.parse_args()

sample_pattern = re.compile(r"^(.+)_S[0-9]+_L[0-9]{3}_(R[0-9]+)_.+\.fastq\.gz$")

def find_fastqs(base_dir, pattern):
    fastq_dict = {}
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            match = pattern.match(filename)
            if match:
                sample_name       = match.group(1)
                sequencing_read   = match.group(2)

                if not sample_name in fastq_dict:
                    fastq_dict[sample_name] = {}
                if not sequencing_read in fastq_dict[sample_name]:
                    fastq_dict[sample_name][sequencing_read] = []
                fastq_dict[sample_name][sequencing_read].append(os.path.join(root, filename))
    return fastq_dict

def merge_fastqs(file_list, output_filename):
    print("Merging:")
    with open(output_filename, 'wb') as output_file:
        for fastq_file_name in file_list:
            print(fastq_file_name)
            with open(fastq_file_name, 'rb') as fastq_file:
                shutil.copyfileobj(fastq_file, output_file)
    print("as {}".format(output_filename))
    print()

fastqs = find_fastqs(args.input_dir, sample_pattern)

for sample in sorted(fastqs.keys()):
    for read in sorted(fastqs[sample].keys()):
        merge_fastqs(sorted(fastqs[sample][read]), os.path.join(args.output_dir, "{}_{}.fastq.gz".format(sample, read)))
