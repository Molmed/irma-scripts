#!/usr/bin/env python

import os
import argparse

def find_runfolders_with_project(project_id):
    incoming_dir = "/proj/ngi2016001/incoming"
    runfolders_with_project = {}
    for runfolder_name in os.listdir(incoming_dir):
        runfolder_path = os.path.join(incoming_dir, runfolder_name)
        unaligned_dir = os.path.join(runfolder_path, "Unaligned")
        
        if os.path.isdir(unaligned_dir):
            for project_dir_name in os.listdir(unaligned_dir):
                if project_dir_name == project_id:
                    runfolder = os.path.basename(runfolder_path)
                    project_path = os.path.join(unaligned_dir, project_dir_name)
                    runfolders_with_project[runfolder] = set(os.listdir(project_path))
                    break
    return runfolders_with_project


def print_result(runfolders):
    all_samples = set() 
    print("\n\nRunfolder\t\t\t\tNr of samples")
    for runfolder, samples in runfolders.items():
        all_samples.update(samples) 
        print(f"{runfolder}\t{len(samples)}")

    print(f"\n{len(all_samples)} unique sample(s) identified on {len(runfolders)} runfolder(s)\n\n")


def main():
    parser = argparse.ArgumentParser(description="Identify runfolders and number of samples associated with a project.")
    parser.add_argument("--project", required=True, help="The project ID to search for.")

    args = parser.parse_args()
    project = args.project

    runfolders = find_runfolders_with_project(project)

    if len(runfolders) == 0:
        print(f"{project} could not be identified in any runfolder.")
    else:
        print_result(runfolders)


if __name__ == "__main__":
    main()
