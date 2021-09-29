import os
import sys
import re

inFile = sys.argv[1]
outFile = sys.argv[2]

sampleDict = {}

with open(inFile, 'r') as fileHandler:

    for line in fileHandler:
        line = line.strip()

        fqpattern = r'^(.*)_(S\d+)_L(\d+)_(R\d)_001.*$'
        fqbasenm = re.match(fqpattern, os.path.basename(line))

        if fqbasenm:
            sample = fqbasenm.group(1)
            ssheet_idx = fqbasenm.group(2)
            laneno = int(fqbasenm.group(3))
            readnr = fqbasenm.group(4)

        else:
            continue

        fcpattern = r'^.*_[AB]?([^_]+)$'
        m = re.match(fcpattern, os.path.basename(os.path.dirname(line)))
        fcid = m.group(1) if m else "NA"

        readgrp = f"{fcid}.{laneno}.{ssheet_idx}"# PU, Plattform unit. Will be used as read tag in BAM-files.

        if readgrp not in sampleDict:
            sampleDict[readgrp] = [sample]
        sampleDict[readgrp].append(line)

with open(outFile, 'w') as outf:

    for readgrp, sample_files in sampleDict.items():
        samplenm = sample_files[0]
        fqfiles = sample_files[1:]
        #Write to .tsv: subject sex status sample PU fastq1 fastq2
        entry = "\t".join([samplenm, "ZZ", "0", samplenm, readgrp] + fqfiles)

        outf.write(f"{entry}\n")