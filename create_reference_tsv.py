import os
import sys
import re
inFile = sys.argv[1]
outFile = sys.argv[2]

sampleDict = {}
outList = []

with open(inFile, 'r') as f:
	lines = f.readlines()
k = 0
for i in lines:
	pattern = r'^(.*)_(S\d+)_L(\d+)_(R\d)_001.*$'
	bnm = re.match(pattern, os.path.basename(i))
	#TODO: 5th field in tsv might later on be changed from an int to a string containing "[FCID].[laneno].[ssheet_idx]".
	# Only applicable on NovaSeq runs. Split below will not work for Miseq runs.
	#fcid = i.split(os.path.sep)[-2].split("_")[-1][1:]

	if bnm:
		sample = bnm.group(1)
		ssheet_idx = bnm.group(2)
		laneno = int(bnm.group(3))
		readnr = bnm.group(4)

	else:
		continue

	if readnr == "R1":
		if sample not in sampleDict:
			sampleDict[sample] = 0
		sampleDict[sample] += 1

		if k != len(lines)-1:
			nxtrd = re.match(pattern, os.path.basename(lines[k+1]))
		if nxtrd.group(4) == "R2":
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i.rstrip("\n"),lines[k+1]))
			outList.append(newline)
		else:
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i))
			outList.append(newline)
		k += 1
	else:
		k += 1
		continue

with open(outFile, 'a') as of:
	of.write(''.join(outList))
