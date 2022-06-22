import os
import re
import sys

"""
Simple script to recreate the custom MultiQC content that the Sarek pipeline generates for the
pipeline_info output
"""


def pipeline_report_header():
    return """
id: 'sarek-summary'
description: " - this information is collected when the pipeline is started."
section_name: 'nf-core/sarek Workflow Summary'
section_href: 'https://github.com/nf-core/sarek'
plot_type: 'html'
data: |
    <dl class=\"dl-horizontal\">
"""


def software_version_header():
    return """
id: 'software_versions'
section_name: 'nf-core/sarek software versions'
section_href: 'https://github.com/nf-core/sarek'
plot_type: 'html'
description: 'are collected at run time from the software output.'
data: |
    <dl class="dl-horizontal">
"""


def pipeline_report_file(d="."):
    return os.path.join(d, "pipeline_report.txt")


def software_version_file(d="."):
    return os.path.join(d, "software_versions.csv")


def pipeline_report_mqc(d="."):
    return os.path.join(d, "workflow_summary_mqc.yaml")


def software_version_mqc(d="."):
    return os.path.join(d, "software_versions_mqc.yaml")


def pipeline_report_pattern():
    return r'^\s+-\s+([^:]+):\s(.+)$'


def software_version_pattern():
    return r'^\s*(\S+)\t+(.*\S)\s*$'


def parse_report_with_pattern(report_file, pattern):
    data = {}
    with open(report_file, "r") as f:
        for g in filter(
                lambda x: x is not None,
                map(
                    lambda x: re.match(pattern, x),
                    f)):
            data[g.group(1)] = g.group(2)
    return data


def write_mqc(mqc_file, header, data):
    with open(mqc_file, "w") as f:
        f.write(header)
        for k, v in data.items():
            f.write(f"        <dt>{k}</dt><dd><samp>{v}</samp></dd>\n")
        f.write("    </dl>\n")


indir = sys.argv[1]
outdir = sys.argv[2]

for header_f, pattern_f, file_f, mqc_f in (
        (pipeline_report_header,
         pipeline_report_pattern,
         pipeline_report_file,
         pipeline_report_mqc),
        (software_version_header,
         software_version_pattern,
         software_version_file,
         software_version_mqc)):
    write_mqc(
        mqc_f(d=outdir),
        header_f(),
        parse_report_with_pattern(
            file_f(d=indir),
            pattern_f()))
