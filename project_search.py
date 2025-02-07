#!/usr/bin/env python

import os
import argparse
import csv

def find_runfolders_with_project(project_id):
    incoming_dir = "/proj/ngi2016001/incoming"
    runfolders_with_project = {}
    for runfolder_name in os.listdir(incoming_dir):
        runfolder_path = os.path.join(incoming_dir, runfolder_name)
        unaligned_dir = os.path.join(runfolder_path, "Unaligned")
        
        if os.path.isdir(unaligned_dir):
            for project_dir_name in os.listdir(unaligned_dir):
                if project_dir_name == project_id:
                    #runfolder = os.path.basename(runfolder_path)
                    project_path = os.path.join(unaligned_dir, project_dir_name)
                    runfolders_with_project[runfolder_path] = set(os.listdir(project_path))
                    break
    return runfolders_with_project


def parse_samplesheet(runfolders, project):
    sample_info = {runfolder: set() for runfolder in runfolders}

    for runfolder in runfolders:
        samplesheet_path = os.path.join(runfolder, "SampleSheet.csv")
        if os.path.exists(samplesheet_path):
            try:
                with open(samplesheet_path, 'r', encoding='utf-8') as fin:
                    reader = csv.reader(fin)
                    sample_name_i = None

                    for row in reader:
                        if "[Data]" in row:
                            header = next(reader)
                            try:
                                sample_name_i = header.index("Sample_Name")
                            except ValueError:
                                print(f"Warning: Sample_Name column not found in {samplesheet_path}")
                                return {}
                            continue
                        if project not in row: continue
                        if sample_name_i is not None and len(row) > sample_name_i: 
                            sample_name = row[sample_name_i]
                            sample_info[runfolder].add(sample_name)
            except Exception as e:
                print(f"Error reading {samplesheet_path}: {e}")
                return {}
        else:
            print(f"Warning: SampleSheet.csv not found in {runfolder}")
            return {}
    return sample_info



def print_result(runfolder, sample_info):
    all_sample_ids = set()
    all_sample_names = set() 
    print("\n\nRunfolder\t\t\t\tSample_ID\tSample_Name")
    for runfolder_path, samples in runfolder.items():
        runfolder = os.path.basename(runfolder_path)
        all_sample_ids.update(samples)
        all_sample_names.update(sample_info[runfolder_path])
        print(f"{runfolder}\t{len(samples)}\t\t{len(sample_info[runfolder_path])}")

    print(f"\n{len(all_sample_ids)} unique sample IDs and {len(all_sample_names)} unique sample names identified on {len(sample_info)} runfolder(s)")


def main():
    parser = argparse.ArgumentParser(description="Find runfolders containing a specific project ID.")
    parser.add_argument("--project", required=True, help="The project ID to search for.")

    args = parser.parse_args()
    project = args.project

    runfolders = find_runfolders_with_project(project)

    if len(runfolders) == 0:
        print(f"{project} could not be identified in any runfolder.")
        return

    sample_info = parse_samplesheet(runfolders, project)
    if len(sample_info) < len(runfolders):
        print("warning..")
    
    print_result(runfolders, sample_info)


if __name__ == "__main__":
    main()
