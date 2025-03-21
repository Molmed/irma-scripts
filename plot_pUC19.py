#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    description="This script finds methylation data in the multiqc results directory created by nf-core methylseq and plots it for pUC19."
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
# Column 4: %CHG (from file 2)
# Column 5: %CHH (from file 2)
# Column 6: %CpG (from file 2)
data1_selected = data1.iloc[:, [0, 1]].copy()
data2_selected = data2.iloc[:, [0, 4, 5, 6]].copy()

# Rename columns to desired names
data1_selected.columns = ["Sample", "Reads"]
data2_selected.columns = ["Sample", "perCHG", "perCHH", "perCpG"]

# Trim the suffix '_1_val_1' from the 'Sample' column using .loc
data1_selected.loc[:, "Sample"] = data1_selected["Sample"].str.replace("_1_val_1", "")
data2_selected.loc[:, "Sample"] = data2_selected["Sample"].str.replace("_1_val_1", "")

# Merge the two DataFrames based on the common column (Sample)
merged_data = pd.merge(data1_selected, data2_selected, on="Sample", how="left")

# Plotting
plt.figure(figsize=(10, 6))


# Define colors based on %CHG, %CHH, and %CpG values
def get_color(row):
    if row["perCHG"] > 1.8 or row["perCHH"] > 1.8 or row["perCpG"] < 96:
        return "red"
    else:
        return "teal"


colors = merged_data.apply(get_color, axis=1)

# Create bar plot
bars = plt.bar(merged_data["Sample"], merged_data["Reads"], color=colors)

# Add horizontal line at y=500
plt.axhline(y=500, color="hotpink", linestyle="--")

# Add labels and title
plt.xlabel("Sample")
plt.ylabel("Reads")
plt.title("pUC19")

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)

# Add values on top of the bars if they are red
for bar, row in zip(bars, merged_data.itertuples()):
    if row.perCHG > 1.8 or row.perCHH > 1.8 or row.perCpG < 96:
        values_to_display = []
        if row.perCHG >= 1.8:
            values_to_display.append(f"{row.perCHG:.1f} %mCHG")
        if row.perCHH >= 1.8:
            values_to_display.append(f"{row.perCHH:.1f} %mCHH")
        if row.perCpG <= 96:
            values_to_display.append(f"{row.perCpG:.1f} %mCpG")
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            "\n".join(values_to_display),
            ha="center",
            va="bottom",
        )

# Add legend
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], color="red", lw=4, label="Failed"),
    Line2D([0], [0], color="teal", lw=4, label="OK"),
]

plt.legend(handles=legend_elements, loc="upper right")

# Save plot to a file in the provided working directory
plt.tight_layout()
plt.savefig(os.path.join(dir, "pUC19.png"))

print(f"The plot has been saved to '{os.path.join(dir, 'pUC19.png')}'.")
