#!/usr/bin/env python

import argparse
import os
import csv
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser(description='Make sample list for sarek multiqc report')
parser.add_argument('-p', '--path', type=str, required=True, help='Path to analysis folder')

args = parser.parse_args()
analysis_path = args.path

def get_sample_names(analysis_path):
    samples = []
    for root, dirs, files in os.walk(analysis_path, followlinks=True):
        for name in files:
            if name.endswith("SampleSheet.csv"):
                file_path = os.path.join(root, name)
                with open(file_path) as f:
                    reader = csv.reader(f, delimiter = ",") 
                    next(reader, None)
                    for row in reader:
                        samples.append(row[0])
    # yield unique sample names
    for sample in sorted(set(samples)):
        yield sample

env = Environment(loader=FileSystemLoader(searchpath=os.path.dirname(os.path.realpath(__file__))))

template = env.get_template('sample_list_template.yaml.j2')
out_file = os.path.join(analysis_path, "sample_list_mqc.yaml")
template.stream(sample_names=get_sample_names(analysis_path)).dump(out_file)

