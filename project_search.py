#!/usr/bin/env python

import os
import argparse
import csv
import sys
from glob import glob

def find_runfolders_with_project(project_id):
    """
    Identifies project folders in the Unaligned directory in runfolders.
    If project_id is found, all sample folders (folder name == Sample ID) 
    for the project are listed
    
    Returns:
        {"Path to runfolder": {Sample_ID1, Sample_ID2}}
    """
    incoming_dir = "/proj/ngi2016001/incoming"
    runfolders_with_project = {}
    for runfolder_name in os.listdir(incoming_dir):
        runfolder_path = os.path.join(incoming_dir, runfolder_name)
        unaligned_dir = os.path.join(runfolder_path, "Unaligned")
        
        if os.path.isdir(unaligned_dir):
            for project_dir_name in os.listdir(unaligned_dir):
                if project_dir_name == project_id:
                    project_path = os.path.join(unaligned_dir, project_dir_name)
                    runfolders_with_project[runfolder_path] = set(os.listdir(project_path))
                    break
    return runfolders_with_project

def parse_samplesheet(runfolders, project):
    """
    Parse sample names and lanes from SampleSheet.csv of each runfolder.

    Returns:
        {runfolder: {"lanes": set(), "sample_nms": set()}}
    """
    sample_info = {runfolder: {"lanes": set(), "sample_nms": set()} for runfolder in runfolders}

    for runfolder in runfolders:
        samplesheet_path = os.path.join(runfolder, "SampleSheet.csv")
        if os.path.exists(samplesheet_path):
            try:
                with open(samplesheet_path, 'r', encoding='utf-8') as fin:
                    reader = csv.reader(fin)
                    sample_name_i = None
                    header_found = False

                    for row in reader:
                        if "[Data]" in row:
                            header_found = True
                            header = next(reader)
                            try:
                                sample_name_i = header.index("Sample_Name")
                                lane_i = header.index("Lane")
                            except ValueError:
                                print(f"Warning: Sample_Name column not found in {samplesheet_path}")
                                return {}
                            continue
                        if project not in row: continue 
                        sample_name = row[sample_name_i]
                        lane = row[lane_i]
                        sample_info[runfolder]["sample_nms"].add(sample_name)
                        sample_info[runfolder]["lanes"].add(lane)
                    if not header_found:
                        print(f"No header found for {samplesheet_path}")
            except Exception as e:
                print(f"Error reading {samplesheet_path}: {e}")
                return {}
        else:
            print(f"Warning: SampleSheet.csv not found in {runfolder}")
            return {}
    return sample_info

def print_result(runfolder, sample_info, fastqs):
    all_sample_ids = set()
    all_sample_names = set()
    all_sample_lanes = []
    print(
        f"\n{'Runfolder':<35} {'Lanes':^10} {'Sample_ID':^10} "
        f"{'Sample_Name':^15} {'R1':^10} {'R2':^10}")
    for runfolder_path, sample_ids in runfolder.items():
        runfolder = os.path.basename(runfolder_path)
        all_sample_ids.update(sample_ids)
        all_sample_names.update(sample_info[runfolder_path]["sample_nms"])
        all_sample_lanes += list(sample_info[runfolder_path]["lanes"])
        nr_sample_ids = len(sample_ids)
        nr_sample_nms = len(sample_info[runfolder_path]["sample_nms"])
        nr_lanes = len(sample_info[runfolder_path]["lanes"])
        r1_nr = len(fastqs[runfolder_path]['R1'])
        r2_nr = len(fastqs[runfolder_path]['R2'])
        print(
            f"{runfolder:<35} {nr_lanes:^10} {nr_sample_ids:^10} "
            f"{nr_sample_nms:^15} {r1_nr:^10} {r2_nr:^10}")

    r1_total = fastqs['Total']['R1']
    r2_total = fastqs['Total']['R2']
    print(
        f"{'Total (unique)':<35} {len(all_sample_lanes):^10} "
        f"{len(all_sample_ids):^10} {len(all_sample_names):^15} "
        f"{r1_total:^10} {r2_total:^10}")

def get_fastqs(runfolders, project):
    fastqs = {runfolder: {"R1": [], "R2": []} for runfolder in runfolders}
    fastqs["Total"] = {"R1": 0, "R2": 0}
    for runfolder in runfolders:
        projpath = os.path.join(runfolder, "Unaligned", project)
        for i in [1, 2]:
            fq = glob(os.path.join(projpath, "**", f"*R{i}*fastq.gz"), recursive=True)
            fastqs[runfolder][f"R{i}"] = [os.path.basename(path) for path in fq]
            fastqs["Total"][f"R{i}"] += len(fq)
    return fastqs

def check_organization(fastqs, org_paths):
    """
    Identifies fastq files not organized in the given paths.

    Returns:
        {org_dir: (runfolder, fq_filename}
    """
    not_organized = {}
    for runfolder_path, fq_filenames in fastqs.items():
        if runfolder_path == "Total":
            continue
        runfolder = os.path.basename(runfolder_path)
        for org_path in org_paths:
            org_dir = os.path.basename(org_path)
            for i in [1, 2]:
                org_fq_paths = glob(os.path.join(org_path, "**", f"*R{i}*fastq.gz"), recursive=True)
                org_fq = {(os.path.basename(os.path.dirname(path)), os.path.basename(path)) for path in org_fq_paths}
                for fq_filename in fq_filenames[f"R{i}"]:
                    if (runfolder, fq_filename) not in org_fq:
                        not_organized.setdefault(org_dir, [])
                        not_organized[org_dir].append((runfolder, fq_filename))
    return not_organized

def main():
    parser = argparse.ArgumentParser(
        description="Find runfolders containing a specific project ID.")
    parser.add_argument(
        "--project", required=True, help="The project ID to search for.")
    parser.add_argument(
        "--check_org",
        required=False,
        help="Check if organizations in /proj/ngi2016001/nobackup/DATA/ "
        "correspond to identified samples and runfolders.\n "
        "Specify an organized folder (e.g., <project>1234) or 'all' to check <project>*",)
    parser.add_argument(
        "--summary_only",
        action="store_true",
        help="Disable listing of fastq files that are not organized in specified folder. "
        "Requires --check_org",)
    args = parser.parse_args()
    
    project = args.project
    check_org = args.check_org
    if check_org == "all":
        check_org = f"{project}*"
    summary_only = args.summary_only
    
    runfolders = find_runfolders_with_project(project)
    if len(runfolders) == 0:
        sys.exit(f"\n{project} could not be identified in any runfolder.")

    sample_info = parse_samplesheet(runfolders, project)
    
    fastqs = get_fastqs(runfolders, project)
    
    print_result(runfolders, sample_info, fastqs)

    if check_org: 
        org_paths = os.path.join(r"/proj/ngi2016001/nobackup/NGI/DATA/", f"{check_org}")
        org_paths = glob(org_paths)
        if len(org_paths) == 0:
            sys.exit(f"\n{project} is not organized in /proj/ngi2016001/nobackup/NGI/DATA/{check_org}")
        
        print("\nChecking organization in\n" + "\n".join(org_paths))
        not_org = check_organization(fastqs, org_paths)
        if len(not_org) == 0:
            for org_path in org_paths:
                org_dir = os.path.basename(org_path)
                print(f"\nAll fastq files are organized for analysis in {org_dir}")
        else:
            print("")
            for org_dir in not_org:
                print(f"{len(not_org[org_dir])} fastq files (R1 + R2) are not organized in {org_dir}")
                if not summary_only:
                    for fq in not_org.get(org_dir, []):
                        print(f"{fq[0]:<35} {fq[1]:<}")
    
    print("")

if __name__ == "__main__":
    main()
