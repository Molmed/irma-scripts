#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    description="This script finds methylation data in the multiqc results directory created by nf-core methylseq and plots the methylation rate in CpG sites for lambda."
)
parser.add_argument("dir", type=str, help="path to analysis directory")
args = parser.parse_args()

# Find the paths to the two files from the provided working directory
dir = args.dir
file1_path = os.path.join(
    dir, "results", "multiqc", "bismark", "multiqc_data", "mqc_bismark_alignment_1.txt"
)
file2_path = os.path.join(
    dir,
    "results",
    "multiqc",
    "bismark",
    "multiqc_data",
    "multiqc_bismark_methextract.txt",
)

# Check if the files exist
if not os.path.exists(file1_path) or not os.path.exists(file2_path):
    print("One or both of the files do not exist. Please check the paths.")
    exit()

# Read the first file with header
data1 = pd.read_csv(file1_path, delimiter="\t")

# Read the second file with header
data2 = pd.read_csv(file2_path, delimiter="\t")

# Select columns by index (assuming 0-based index)
# Column 0: Sample (from both files)
# Column 1: Reads (from file 1)
# Column 6: %CpG (from file 2)
data1_selected = data1.iloc[:, [0, 1]].copy()
data2_selected = data2.iloc[:, [0, 6]].copy()

# Rename columns to desired names
data1_selected.columns = ["Sample", "Reads"]
data2_selected.columns = ["Sample", "%CpG"]

# Trim the suffix '_1_val_1' from the 'Sample' column using .loc
data1_selected.loc[:, "Sample"] = data1_selected["Sample"].str.replace("_1_val_1", "")
data2_selected.loc[:, "Sample"] = data2_selected["Sample"].str.replace("_1_val_1", "")

# Merge the two DataFrames based on the common column (Sample)
merged_data = pd.merge(data1_selected, data2_selected, on="Sample", how="left")

# Plotting
plt.figure(figsize=(10, 6))


# Define colors based on %CpG values
def get_color(value):
    if value <= 0.7:
        return "hotpink"
    elif value <= 1:
        return "orange"
    else:
        return "red"


colors = merged_data["%CpG"].apply(get_color)

# Create bar plot
bars = plt.bar(merged_data["Sample"], merged_data["Reads"], color=colors)

# Add horizontal line at y=5000
plt.axhline(y=5000, color="teal", linestyle="--")

# Add labels and title
plt.xlabel("Sample")
plt.ylabel("Reads")
plt.title("Lambda")

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)

# Add %CpG values on top of the bars if they are over 0.7
for bar, value in zip(bars, merged_data["%CpG"]):
    if value > 0.7:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f} %mCpG",
            ha="center",
            va="bottom",
        )

# Add legend
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], color="hotpink", lw=4, label="OK"),
    Line2D([0], [0], color="orange", lw=4, label="<1.0"),
    Line2D([0], [0], color="red", lw=4, label="Failed"),
]

plt.legend(handles=legend_elements, loc="upper right")

# Save plot to a file in the provided working directory
plt.tight_layout()
plt.savefig(os.path.join(dir, "lambda.png"))

print(f"The plot has been saved to '{os.path.join(dir, 'lambda.png')}'.")
