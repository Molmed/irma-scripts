import sys
import os
import csv
import argparse
import yaml
from glob import glob

class QC:
    """
    QC criteria for BPA of WGS projects according to INS-00123 v.25.0
    """
    def __init__(self):
        self.insert_size = (317, 428)
        self.variants = (4800000, 5300000)
        self.gc = (40.5, 42.1)
        self.percent_mapped = (97.1, 100)
        self.cov_10_x = (91, float('inf'))
        self.cov_30_x = (58, float('inf'))
        self.version = "v.25.0"  # Document version INS-00123

    def limits(self, metric):
        if metric == "Coverage ≥10 X":
            return self.cov_10_x
        elif metric == "Coverage ≥30 X":
            return self.cov_30_x
        elif metric == "Unfiltered variants":
            return self.variants
        elif metric == "Average GC %":
            return self.gc
        elif metric == "% Mapped":
            return self.percent_mapped
        elif metric == "Average insert size":
            return self.insert_size
        else:
            return ("N/A", "N/A")
    
    def pretty_limits(self, metric):
        lt, ut = self.limits(metric)
        if "Cov" in metric:
            return f"≥ {lt} X"
        elif metric == "Unfiltered variants":
            return f"{lt / 1000000:.1f}-{ut / 1000000:.1f} M"
        elif metric == "Average GC %":
            return f"{lt}-{ut} %"
        elif metric == "% Mapped":
            return f"{lt} %"
        elif metric == "Average insert size":
            return f"{lt}-{ut} nt"
        else:
            return f"QC thresholds not found"
    
    def pretty_val(self, metric, value):
        if "Cov" in metric:
            return f"{value} X"
        elif metric == "Unfiltered variants":
            return f"{value / 1000000:.1f} M"
        elif metric in ["Average GC %", "% Mapped"]:
            return f"{value} %"
        elif metric == "Average insert size":
            return f"{value} nt"
        else:
            return f"{value}"
        
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to calculate additional metrics and produce custom data files for MultiQC report after WGS analysis with sarek >=3.4.2"
    )
    parser.add_argument(
        "--analysis_dir",
        required=True,
        help="Path to sarek analysis result folder is located",
    )
    parser.add_argument("--project", required=True, help="Project name")
    args = parser.parse_args()
    return args


def find_reports(analysis_dir):
    """
    Attempts to locate the necessary reports used to generate the extra metrics to 
    include in MultiQC report. If some, but not all, reports are found the script
    will continue but print a warning. 

    Args:
        analysis_dir (str): Path to the analysis directory where sarek results folder is located.

    Returns:
        dict: Paths to reports.
        None: If no reports where found.
    """

    report_folder = os.path.join(analysis_dir, "results/reports/")
    search_paths = {
        "mosdepth_sum": os.path.join(report_folder, "mosdepth/*/*.md.mosdepth.summary.txt"),
        "mosdepth_reg": os.path.join(report_folder, "mosdepth/*/*.md.mosdepth.region.dist.txt"),
        "samstat": os.path.join(report_folder, "samtools/*/*.md.cram.stats"),
        "snpeff": os.path.join(report_folder, "snpeff/haplotypecaller/*/*_snpEff.csv")
    }
    
    report_paths = {
        report_type: glob(path) for report_type, path in search_paths.items()
    }
    
    missing_reports = [report_type for report_type, paths in report_paths.items() if len(paths) == 0]
    
    if 0 <= len(missing_reports) < 4:
        print(f"Using reports in {os.path.dirname(report_folder)}")
        for report in missing_reports:
            print(f"Warning! No reports found in {search_paths[report]}")
        return report_paths
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
            avg_cov[sample] = round(bases / length)
    return avg_cov

def get_samstats(reports):
    """
    Collect precalculated values for average insert size and calculates 
    average GC % and % mapped reads.

    Args:
        reports (list): List of paths to Samtools stats reports
    
    Returns:
        dict: One dict for each metric
    """
    gc_avg, aln_percent, insert_sizes = {}, {}, {}
    for report in reports:
        sample = os.path.basename(os.path.dirname(report))    
        total_gc_percentage = 0.0
        total_reads = 0.0
        with open(report) as fin:
            for line in fin:
                if line.startswith('GCF') or line.startswith('GCL'):
                    identifier, gc_percentage, num_reads = line.strip().split('\t')
                    total_gc_percentage += float(gc_percentage) * float(num_reads)
                    total_reads += float(num_reads)
                elif line.startswith('SN\tinsert size average:'):
                    insert_avg = round(float(line.strip().split('\t')[2]))
                    insert_sizes[sample] = insert_avg
                elif line.startswith('SN\treads mapped:'):
                    total_mapped = float(line.strip().split('\t')[2])
        
        gc_avg[sample] = round(total_gc_percentage / total_reads)
        aln_percent[sample]= round(total_mapped / total_reads * 100, 1)
    return gc_avg, aln_percent, insert_sizes

def extra_genstats_out(sample_data):
    """
    Collects data to be presented in the General stats table and format it
    to enable yaml output.

    Args:
        sample_data (dict): Dictionary containing all parsed metrics
    
    Returns:
        dict: Metrics for General stats redy for yaml.dump
    """
    data = {
    "custom_data": {
        "extra_stats": {
            "plot_type": "generalstats",
            "headers": {
                    "Average_insert_size": {"max": 800, "min": 0, "suffix": "nt"},
                    "Average_GC_%": {"max": 100, "min": 0, "suffix": "%"},
                    "Autosomal_coverage": {"suffix": "X"}
                },
            "data": {}
        }                
    }}
    metrics = ["Average insert size", "Average GC %", "Autosomal coverage"]
    for metric in metrics:
        for sample, value in sample_data[metric].items():
            header = "_".join(metric.split())
            data["custom_data"]["extra_stats"]["data"].setdefault(sample, {})[header] = value
    return data

def QC_out(qc_fail, qc):
    """
    Collects samples that failed QC and format it to enable yaml output.


    Args:
        qc_fail (dict): Metric information for samples that failed QC
        qc (QC object): QC thresholds and functions for pretty formatting

    Returns:
       dict: QC information ready for yaml.dump
    
    Returns:
        dict: Metrics for General stats redy for yaml.dump

    """
    version = qc.version
    yaml_out = {
            "id": "qc_list",
            "section_name": "QC check",
            "plot_type": "html",
            "description": f"List of samples that fail QC criteria according to INS-00123 {version}.",
            "data": "\n<ul>\n"}
    if len(qc_fail) != 0:
        for metric in qc_fail:
            limits = qc.pretty_limits(metric)
            yaml_out["data"] += f"<li>{metric} ({limits})</li>\n<ul>\n"
            for sample, value in qc_fail[metric]:
                fail_val = qc.pretty_val(metric, value)
                yaml_out["data"] += f"<li>{sample} ({fail_val})</li>\n"
            yaml_out["data"] += "</ul>\n"
    else:
        yaml_out["data"] += "<li>All sample passed QC!</li>\n"
    yaml_out["data"] += "</ul>"

    return yaml_out 


def check_qc(data, qc):
    """
    Checks QC metrics against specified thresholds.

    Args:
        data (dict): Dictionary containing all parsed metrics
        qc_ranges (QC object): QC thresholds and functions for pretty formating

    Returns:
        dict: Metric(s), sample(s) and value(s) that failed QC
    """
    failed_metrics = {}
    for metric in data:
        lt, ut = qc.limits(metric)
        if lt == "N/A":
            continue
        for sample, value in data[metric].items():
            if not lt <= value <= ut:
                failed_metrics.setdefault(metric, []).append((sample, value))
    return failed_metrics

def get_x_cov(reports, coverage):
    """
    Parse precalculated values for proportion of reference with a specific coverage
    from mosdepth report. The proportion is then converted to percentage.

    Args:
        reports (list): Paths to mosdepth reports
        coverage (int): The coverage of interest
    
    Returns:
        dict: Percentage at specified coverage per sample
    """
    data = {}
    for report in reports:
        sample = os.path.basename(os.path.dirname(report))
        with open(report) as fin:
            cov = csv.reader(fin, delimiter="\t")
            for row in cov:
                cov_region = row[0]
                cov_x = int(row[1])
                proportion = float(row[2])
                if cov_region == "total" and cov_x == coverage:
                    data[sample] = proportion * 100
    return data

def get_number_variants(reports):
    """
    Parse precalculated values for number of unfiltered variants from
    snpEff reports.

    Args:
        reports (list): Paths to snpEff reports
    
    Returns:
        dict: Number of unfiltered variants per sample
    """
    data = {}

    for report in reports:
        sample = os.path.basename(os.path.dirname(report))
        with open(report) as fin:
            for line in fin:
                if line.startswith("Number_of_variants_before_filter,"):
                    data[sample] = int(line.strip().split(", ")[1])
    return data

def collect_data(reports):
    """
    Function to parse and collect all metrics.

    Args:
        reports (dict): Paths to reports by report type

    Returns:
       dict: All parsed metrics for each sample
    """
    gc_avg, aln_percent, insert_sizes = get_samstats(reports["samstat"])
    data = {
        "Autosomal coverage": calculate_avg_coverage(reports["mosdepth_sum"]),
        "Coverage ≥10 X": get_x_cov(reports["mosdepth_reg"], 10),
        "Coverage ≥30 X": get_x_cov(reports["mosdepth_reg"], 30),
        "Unfiltered variants": get_number_variants(reports["snpeff"]),
        "Average GC %": gc_avg,
        "% Mapped": aln_percent,
        "Average insert size": insert_sizes
    }
    return data

def main():

    args = parse_arguments()
    analysis_dir = args.analysis_dir
    project = args.project
    qc = QC()
    reports = find_reports(analysis_dir)
    if not reports:
        sys.exit(1)
    
    all_data = collect_data(reports)
    qc_fail = check_qc(all_data, qc) 
    qc_out = QC_out(qc_fail, qc)
    extra_genstats = extra_genstats_out(all_data)

    with open(os.path.join(analysis_dir, "QC_list_mqc.yaml"), "w") as fout:
        yaml.dump(qc_out, fout)
    with open(os.path.join(analysis_dir, "extra_stats.yaml"), "w") as fout:
        yaml.dump(extra_genstats, fout)

if __name__ == "__main__":
    main()

