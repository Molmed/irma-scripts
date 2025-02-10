#!/usr/bin/env python

import os
import sys
import re

fqdir = sys.argv[1]
outfile = sys.argv[2]

sampledict = {}
fqpattern = r'^(.*)_(S\d+)_L(\d+)_(R\d)_001.*$'
fcpattern = r'^.*_[AB]?([^_]+)$'


for root, dirs, fqlinks in os.walk(fqdir):
    for link in fqlinks:
        fqpath = os.readlink(os.path.join(root, link))
        fqbasenm = re.match(fqpattern, link)

        if fqbasenm:
            sample = fqbasenm.group(1)
            ssheet_idx = fqbasenm.group(2)
            laneno = int(fqbasenm.group(3))
            readnr = fqbasenm.group(4)

        else:
            continue

        m = re.match(fcpattern, root)
        fcid = m.group(1) if m else "NA"

        readgrp = f"{fcid}.{laneno}.{ssheet_idx}"  # PU, Plattform unit. Will be used as read tag in BAM-files.

        sampledict.setdefault(readgrp, {"sample": sample, "R1": "", "R2": ""})
        sampledict[readgrp][readnr] = fqpath

with open(outfile, 'w') as fout:
    fout.write("patient,sample,lane,fastq_1,fastq_2\n")
    for readgrp, data in sampledict.items():
        samplenm = data["sample"]
        R1 = data["R1"]
        R2 = data["R2"]
        entry = ",".join([samplenm, samplenm, readgrp, R1, R2])
        fout.write(f"{entry}\n")
