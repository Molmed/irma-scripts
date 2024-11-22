#!/usr/bin/env python

import os
import sys
import argparse
import shutil
import csv
from glob import glob


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Organize flowcell for a specific project"
    )
    parser.add_argument(
        "--runfolder", type=str, required=True, help="Path to runfolder (required)"
    )
    parser.add_argument(
        "--project", type=str, required=True, help="Project name (required)"
    )
    parser.add_argument(
        "--base_data_path",
        type=str,
        required=False,
        default="/proj/ngi2016001/nobackup/NGI/DATA",
        help="Path where flowcell will be organized (default: %(default)s)",
    )
    parser.add_argument(
        "--exclude_lane",
        type=str,
        required=False,
        default="",
        help="Lane number(s) to exclude (optional). 2,8..",
    )
    parser.add_argument(
        "--exclude_sample",
        type=str,
        required=False,
        default="",
        help="Sample name(s) to exclude (optional). Sample-1,Sample-2..",
    )
    parser.add_argument(
        "--exclude_sampleID",
        type=str,
        required=False,
        default="",
        help="Sample ID(s) to exclude (optional). Sample-1,Sample-2..",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        required=False,
        help="Add suffix to output-folder (Project_suffix)",
    )
    parser.add_argument(
        "--force",
        required=False,
        action="store_true",
        help="Force organization of runfolder. Previous runfolder organization will be removed.",
    )
    return parser.parse_args()


def parse_samplesheet(
    samplesheet, project, exclude_lane, exclude_sample, exclude_sampleID
):
    sample_info = {}

    lane_i, sample_id_i, sample_name_i, description_i = None, None, None, None

    try:
        with open(samplesheet) as fin:
            samplesheet = csv.reader(fin)

            for row in samplesheet:
                if "[Data]" in row:
                    header = next(samplesheet)
                    lane_i = header.index("Lane")
                    sample_id_i = header.index("Sample_ID")
                    sample_name_i = header.index("Sample_Name")
                    description_i = header.index("Description")
                    continue

                if project not in row:
                    continue

                lane, sample_id, sample_name = (
                    row[lane_i],
                    row[sample_id_i],
                    row[sample_name_i],
                )
                include = not (
                    lane in exclude_lane
                    or sample_id in exclude_sampleID
                    or sample_name in exclude_sample
                )

                if include:
                    description = dict(
                        item.split(":") for item in row[description_i].split(";")
                    )
                    library_name = description["LIBRARY_NAME"]
                    sample_info.setdefault(sample_id, {})[sample_name] = [
                        lane,
                        library_name,
                    ]

    except csv.Error as e:
        print(f"Error parsing SampleSheet.csv: {e}")

    return sample_info


def organize_files(sample_info, runfolder_path, project, data_path):
    runfolder = os.path.basename(runfolder_path)
    for sample_id, samples in sample_info.items():
        for sample_name, (lane, library_name) in samples.items():
            fq_folder = os.path.join(runfolder_path, "Unaligned", project, sample_id)
            src_path = glob(os.path.join(fq_folder, "*fastq.gz"))
            if src_path:
                dst_path = os.path.join(data_path, sample_name, library_name, runfolder)
                os.makedirs(dst_path, exist_ok=True)
                for fastq in src_path:
                    symlink(dst_path, fastq)
            else:
                print(f"No fastq.gz files found in {fq_folder}")


def symlink(dst_path, fastq):
    if os.path.exists(fastq):
        fq_name = os.path.basename(fastq)
        dst_file = os.path.join(dst_path, fq_name)
        try:
            os.symlink(fastq, dst_file)
        # Should catch possible permission issues
        except OSError as e:
            print(f"Error creating symlink: {e}")
    else:
        print(f"No symlink created for {fastq}. File not found.")


def check_paths(runfolder_path, fastq_path, samplesheet, data_path, project, force):
    if not os.path.exists(runfolder_path):
        raise FileNotFoundError(f"{runfolder_path} not found.")
    if not os.path.exists(fastq_path):
        raise FileNotFoundError(f"Project {project} not found in {runfolder_path}.")
    if not os.path.exists(samplesheet):
        raise FileNotFoundError(f"No sample sheet found for {runfolder_path}.")

    organized_data = glob(
        os.path.join(data_path, "*/*", os.path.basename(runfolder_path))
    )
    if organized_data:
        if force:
            remove_organized(organized_data)
        else:
            raise Exception("Flowcell already organized for this project.")


def remove_organized(organized_data):
    for path in organized_data:
        # Remove folder and symlinks
        shutil.rmtree(path)
        clean_empty_parent_dirs(path)


def clean_empty_parent_dirs(path):
    parent_dir = os.path.dirname(path)
    if len(os.listdir(parent_dir)) == 0:
        os.rmdir(parent_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    if len(os.listdir(grandparent_dir)) == 0:
        os.rmdir(grandparent_dir)


def main():
    args = parse_arguments()
    runfolder_path = args.runfolder
    project = args.project
    exclude_lane = args.exclude_lane.split(",")
    exclude_sample = args.exclude_sample.split(",")
    exclude_sampleID = args.exclude_sampleID.split(",")
    base_data_path = args.base_data_path
    suffix = args.suffix
    force = args.force

    outdir = project
    if suffix:
        outdir += f"_{suffix}"
    data_path = os.path.join(base_data_path, outdir)
    fastq_path = os.path.join(runfolder_path, "Unaligned", project)
    samplesheet = os.path.join(runfolder_path, "SampleSheet.csv")

    try:
        check_paths(runfolder_path, fastq_path, samplesheet, data_path, project, force)
    except (FileNotFoundError, Exception) as e:
        print(f"Something went wrong: {e}")
        sys.exit(1)

    sample_info = parse_samplesheet(
        samplesheet, project, exclude_lane, exclude_sample, exclude_sampleID
    )

    organize_files(sample_info, runfolder_path, project, data_path)


if __name__ == "__main__":
    main()
