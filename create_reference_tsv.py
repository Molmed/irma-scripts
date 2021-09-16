import sys
inFile = sys.argv[1]
outFile = sys.argv[2]

sampleDict = {}

with open(inFile, 'r') as f:
	lines = f.readlines()

k = 0
for i in lines:
	sample = i.split('/')[-1].split('_')[0]
	readnr = i.split('/')[-1].split('_')[3]
	if sample in sampleDict and readnr == "R1":
		sampleDict[sample] = sampleDict[sample] + 1
		if k != len(lines)-1:
			nextread = lines[k+1].split('/')[-1].split('_')[3]
		if nextread == "R2":
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i.rstrip("\n"),lines[k+1]))
		else:
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i))

		with open(outFile, 'a') as of:
			of.write(newline)

	elif sample not in sampleDict and readnr == "R1":
		sampleDict[sample] = 1
		if k != len(lines)-1:
			nextread = lines[k+1].split('/')[-1].split('_')[3]
		if nextread == "R2":
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i.rstrip("\n"),lines[k+1]))
		else:
			newline = '\t'.join((sample,"ZZ","0",sample,str(sampleDict[sample]),i))

		with open(outFile, 'a') as of:
			of.write(newline)
	k= k+1

