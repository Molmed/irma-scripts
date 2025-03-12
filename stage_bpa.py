#!/usr/bin//env python

import argparse
import os
import shutil
import glob
import subprocess

class Stager:
    def __init__(self, project, pipeline, analysis_dir, results_dir, stage_dir, config, wes=False, force=False):
        self.project = project
        self.pipeline = pipeline
        self.force = force
        self.config = config
        self.wes = wes
        self.analysis_dir = analysis_dir
        self.stage_dir = stage_dir
        self.results_dir = results_dir
        self.readme = os.path.join(config["readme_dir"], self._get_readme())

    def run(self):
        try:
            self._check_analysis()
            if self._check_staging() and not self.force:
                print(f"Project {self.project} already staged. Use --force to overwrite.")
                return 0

            self._prepare_for_staging()
            self._stage_files()
            self._calculate_checksums()
            delivery_readme = os.path.join(self.stage_dir, os.path.basename(self.readme))
            print(f"Project {self.project} staged successfully!\n")
            print("Before delivery:")
            print(f"Eensure that there are no errors in {self.config['checksums_log']}")
            print(f"Make sure that information in {delivery_readme} is correct.")
            print(f"  Note. Remember to update cheksum for README if you make any changes.\n")
            print(f"Make README available to the project coordinators:")
            print(f"  cp {delivery_readme} /proj/ngi2016001/incoming/reports/{self.project}/\n")
            return 0

        except Exception as e:
            print(f"Error: {e}")
            return 1 

    def _check_analysis(self):
        if not os.path.exists(self.results_dir):
            raise FileNotFoundError(f"results directory not found: {self.analysis_dir}")

    def _check_staging(self):
        return os.path.exists(self.stage_dir)

    def _prepare_for_staging(self):
        match self.pipeline:
            case "sarek":
                self._prepare_sarek()
            case "rnaseq" | "methylseq":
                self._tar_qualimap()

    def _prepare_sarek(self):
        """
        Prepare sarek result dir for staging.
          - Move markduplicates from results --> analysis dir
          - Exchange sarek generated multiQC with custom report
        """
        try:
            # move markduplicate files from results to analysis dir
            if os.path.exists(self.config["md_src"]):
                shutil.move(self.config["md_src"], self.config["md_dest"])

            if not os.path.exists(self.config["custom_report"]):
                print(f"Custom multiQC report not found in {self.config['custom_report']}. Staging with pipeline generated report.")
                return
            
            # Replace pipeline generated multiQC with custom
            
            for f in glob.glob(os.path.join(self.config["sarek_multiqc"], "*")):
                os.remove(f)
            report_replc = os.path.join(self.config["sarek_multiqc"], os.path.basename(self.config["custom_report"]))
            data_replc = os.path.join(self.config["sarek_multiqc"], os.path.basename(self.config["custom_data"]))
            shutil.copy(self.config["custom_report"], report_replc)
            shutil.copy(self.config["custom_data"], data_replc)
            
        except Exception as e:
            raise RuntimeError(f"Sarek preparation failed: {e}")

    def _tar_qualimap(self):
        """
        Prepare rnaseq and methylseq result dir for staging
          - Compress qualimap dir
          - remove original qualimap dir
        """
        try:
            qualimap_dir = self.config[f"{self.pipeline}_qualimap"]
            if os.path.exists(qualimap_dir):
                tar_command = ["tar", "-czvf", f"{qualimap_dir}.tar.gz", qualimap_dir]
                subprocess.run(tar_command, check=True)
                shutil.rmtree(qualimap_dir)
        
        except Exception as e:
            raise RuntimeError(f"{self.pipeline} prerparation failed: {e}")

    def _stage_files(self):
        """
        Stage files for delivery.
          - Copy pipeline specific README
          - Symlink project result dir
        """
        if self.force and os.path.exists(self.stage_dir):
            shutil.rmtree(self.stage_dir)
        os.makedirs(self.stage_dir)
        try:
            shutil.copy(self.readme, self.stage_dir)
            folder_name = os.path.basename(self.results_dir)
            os.symlink(self.results_dir, os.path.join(self.stage_dir, folder_name))
        except Exception as e:
            raise RuntimeError(f"Staging failed: {e}")

    def _get_readme(self):
        match self.pipeline:
            case "rnaseq":
                return self.config["readme_rna"]
            case "methylseq":
                return self.config["readme_meth"]
            case "sarek":
                if self.wes:
                    return self.config["readme_wes"]
                else:
                    return self.config["readme_wgs"]


    def _calculate_checksums(self):
        """
        Submits a Slurm job to calculate checksums.

        Raises:
            RuntimeError: If any error occurs during job submission.
        """

        try:
            sbatch_command = [
                "sbatch",
                "-A", self.config["slurm_account"],
                "-n", self.config["slurm_nodes"],
                "-t", self.config["slurm_time" ],
                "-J", f"checksums_{self.project}",
                "-o", self.config["checksums_log"],
                "--wrap",
                (
                    f"find -L {self.stage_dir} -not -type d -not -name 'checksums.md5' | "
                    f"xargs -P{self.config['slurm_nodes']} md5sum >> {self.config['checksums']}"
                ),
            ]

            result = subprocess.run(sbatch_command, capture_output=True, text=True, check=True)

            print(result.stdout)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Slurm job submission failed: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Stage BPA results for delivery.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
    parser.add_argument(
        "--pipeline",
        required=True,
        choices=["sarek", "rnaseq", "methylseq"],
        help="Pipeline used for analysis.")
    parser.add_argument(
            "--project",
            required=True,
            help="Name of project to be staged for delivery")
    parser.add_argument(
            "--wes",
            action="store_true",
            help="Stage WES analysis. Requires --pipeline=sarek")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite previous staging.")
    parser.add_argument(
        "--analysis_path",
        default="/proj/ngi2016001/nobackup/NGI/ANALYSIS",
        help="Path to where project folder to be staged is located.")
    parser.add_argument(
        "--delivery_path",
        default="/proj/ngi2016001/nobackup/NGI/DELIVERY",
        help="Path to where staging should be performed")
    args = parser.parse_args()

    project = args.project
    pipeline = args.pipeline
    wes = args.wes
    force = args.force
    analysis_dir = os.path.join(args.analysis_path, project)
    stage_dir = os.path.join(args.delivery_path, project)
    results_dir = os.path.join(analysis_dir, "results")

    config = {
        "md_src": os.path.join(results_dir, "preprocessing/markduplicates"),
        "md_dest": os.path.join(analysis_dir, "markduplicates"),
        "sarek_multiqc": os.path.join(results_dir, "reports/multiqc"),
        "custom_report": os.path.join(analysis_dir, f"multiqc_ngi/{project}_multiqc_report.html"),
        "custom_data": os.path.join(analysis_dir, f"multiqc_ngi/{project}_multiqc_report_data.zip"),
        "rnaseq_qualimap": os.path.join(results_dir, "star_salmon/qualimap"),
        "methylseq_qualimap": os.path.join(results_dir, "qualimap"),
        "checksums_log": os.path.join(analysis_dir, "logs/checksums.log"),
        "checksums": os.path.join(stage_dir, "checksums.md5"),
        "slurm_account": "ngi2016001",
        "slurm_nodes": "8",
        "slurm_time": "10:00:00",
        "readme_dir": "/proj/ngi2016001/nobackup/NGI/softlinks",
        "readme_rna": "DELIVERY.README.RNASEQ.md",
        "readme_meth": "DELIVERY.README.METHYLSEQ.md",
        "readme_wgs": "DELIVERY.README.SAREK.md",
        "readme_wes": "DELIVERY.README.SAREK.WES.md",
    }

    stager = Stager(project, pipeline, analysis_dir, results_dir, stage_dir, config, wes, force)
    exit_code = stager.run()
    exit(exit_code)

if __name__ == "__main__":
    main()
