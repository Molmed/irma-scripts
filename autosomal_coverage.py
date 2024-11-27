#!/usr/bin/env python

import sys
import os
import csv
import argparse
from glob import glob


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to calculate mean autosomal coverage after Sarek3.4.2 WGS analyses"
    )
    parser.add_argument(
        "--analysis_dir",
        required=False,
        default="/proj/ngi2016001/nobackup/NGI/ANALYSIS",
        help=f"Path to analysis folder. (default: %(default)s)",
    )
    parser.add_argument("--project", required=True, help="Project name")
    args = parser.parse_args()
    return args


def find_reports(project_dir, analysis_dir, project):
    """
    Tries to find the Mosdepth reports in the specified directories.
    In most cases the reports should be located in the project_dir.

    Args:
        project_dir (str): Path to the project directory.
        analysis_dir (str): Path to the analysis directory.
        project (str): Project name

    Returns:
        str: Path to the found Mosdepth reports directory.
        str: Path to where output will be written.
        None: If the reports cannot be found in either directory.
    """

    for dir_path in [project_dir, analysis_dir]:
        report_folder = os.path.join(dir_path, "results/reports/mosdepth")
        reports = glob(os.path.join(report_folder, "*/*.md.mosdepth.summary.txt"))
        if len(reports) != 0:
            print(f"Calculating autosomal coverage base on reports in {report_folder}")
            outfile = os.path.join(dir_path, f"{project}_autsomal_coverage.txt")
            return reports, outfile
        else:
            print(f"No reports found in {report_folder}")

    return None


def calculate_avg_coverage(reports):
    """
    Calculates average autosomal coverage for each sample.

    Args:
        reports (list): List of paths to Mosdepth summary reports

    Returns:
        dict: Sample(s) (key), average_coverage (value)
    """
    auto_chroms = [f"chr{x}" for x in range(1, 23)]
    avg_cov = {}

    for report in reports:
        sample = os.path.basename(os.path.dirname(report))
        bases = 0
        length = 0
        with open(report) as fin:
            cov = csv.reader(fin, delimiter="\t")
            header = next(cov)
            chrom_index = header.index("chrom")
            length_index = header.index("length")
            bases_index = header.index("bases")
            for row in cov:
                if row[chrom_index] in auto_chroms:
                    bases += int(row[bases_index])
                    length += int(row[length_index])
            avg_cov[sample] = str(bases / length)
    return avg_cov


def main():

    args = parse_arguments()
    analysis_dir = args.analysis_dir
    project = args.project
    project_dir = os.path.join(analysis_dir, project)

    reports, outfile = find_reports(project_dir, analysis_dir, project)
    if not reports:
        sys.exit(1)
    avg_cov = calculate_avg_coverage(reports)

    with open(outfile, "w") as fout:
        fout.write("Sample\tAvg. cov\n")
        for sample in avg_cov:
            fout.write(f"{sample}\t{avg_cov[sample]}\n")

    print(f"Results written to {outfile}")


if __name__ == "__main__":
    main()
