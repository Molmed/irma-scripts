#!/usr/bin/env python

import os
import sys
import argparse
from glob import glob

def parse_arguments():
    parser = argparse.ArgumentParser(description='Organize flowcell for a specific project in /proj/ngi2016001/nobackup/NGI/DATA/<project>')
    parser.add_argument('--runfolder', type=str, required=True, help='Name of runfolder (required)')
    parser.add_argument('--project', type=str, required=True, help='Project name (required)')
    parser.add_argument('--exclude_lane', type=str, required=False, default='', help='Lane number(s) to exclude (optional).')
    parser.add_argument('--exclude_sample', type=str, required=False, default='', help='Sample name(s) to exclude (optional). Sample-1,Sample-2..')
    parser.add_argument('--exclude_sampleID', type=str, required=False, default='', help='Sample ID(s) to exclude (optional). Sample-1,Sample-2..')
    parser.add_argument('--suffix', type=str, required=False, help='Add suffix to output-folder (Project_suffix).')
    return parser.parse_args()

def get_sample_info(line, exclude_lane, exclude_sample, exclude_sampleID):
    lane, sample_id, sample_name, *_, library_info = line.split(',')
    library_name = library_info.split(':')[-1].strip()
    include = not (lane in exclude_lane or sample_id in exclude_sampleID or sample_name in exclude_sample)
    return lane, sample_id, sample_name, library_name, include

def parse_samplesheet(samplesheet, project, exclude_lane, exclude_sample, exclude_sampleID):
    sample_info = {}
    with open(samplesheet) as fin:
        for line in fin:
            if project not in line:
                continue
            lane, sample_id, sample_name, library_name, include = get_sample_info(line, exclude_lane, exclude_sample, exclude_sampleID)
            if include:
                sample_info.setdefault(lane, {})[library_name] = [sample_id, sample_name]
    return sample_info

def organize_files(sample_info, runfolder_path, project, data_path, runfolder):
    for lane, libraries in sample_info.items():
        for library_name, (sample_id, sample_name) in libraries.items():
            src_path = glob(os.path.join(runfolder_path, 'Unaligned', project, sample_id, '*fastq.gz'))
            dst_path = os.path.join(data_path, sample_name, library_name, runfolder)
            os.makedirs(dst_path, exist_ok=True)
            for fastq in src_path:
                fq_name = os.path.basename(fastq)
                os.symlink(fastq, os.path.join(dst_path, fq_name))

def check_paths(runfolder_path, fastq_path, samplesheet, data_path, runfolder):
    if not os.path.exists(runfolder_path):
        raise FileNotFoundError(f'Runfolder {runfolder} not found.')
    if not os.path.exists(fastq_path):
        raise FileNotFoundError(f'Project {project} not found in {runfolder}.')
    if not os.path.exists(samplesheet):
        raise FileNotFoundError(f'No sample sheet found for {runfolder}.')
    if glob(os.path.join(data_path, '*/*', runfolder)):
        raise Exception('Flowcell already organized for this project.')

def main():
    # Parse command line arguments
    args = parse_arguments()
    runfolder = args.runfolder
    project = args.project
    exclude_lane = args.exclude_lane.split(',')
    exclude_sample = args.exclude_sample.split(',')
    exclude_sampleID = args.exclude_sampleID.split(',')
    suffix = args.suffix

    # Set up in- and output paths
    outdir = project
    if suffix:
        outdir += f'_{suffix}'
    runfolder_path = os.path.join('/proj', 'ngi2016001', 'incoming', runfolder)
    fastq_path = os.path.join(runfolder_path, 'Unaligned', project)
    data_path = os.path.join('/proj', 'ngi2016001', 'nobackup', 'NGI', 'DATA', outdir)
    samplesheet = os.path.join(runfolder_path, 'SampleSheet.csv')

    # Check that in- and output paths are OK
    try:
        check_paths(runfolder_path, fastq_path, samplesheet, data_path, runfolder)
    except (FileNotFoundError, Exception) as e:
        print(f'Something went wrong: {e}')
        sys.exit(1)
    
    # Collect sample infor from SampleSheet.csv
    sample_info = parse_samplesheet(samplesheet, project, exclude_lane, exclude_sample, exclude_sampleID)
    
    # Symlink fastq files to /proj/ngi2016001/nobackup/NGI/DATA/<outdir>/<sample>/<library name>/<runfolder>
    organize_files(sample_info, runfolder_path, project, data_path, runfolder)

if __name__ == "__main__":
    main()

