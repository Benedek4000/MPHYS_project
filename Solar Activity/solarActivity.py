import numpy as np
import solar_constants as constants
from spacepy import pycdf

noOfLinesBeforeData = 3

#READING TXT FILE
lines = []
data = []
fullData = []
with open(constants.RdatafileName, 'r') as f:
    for i in f:
        i = i[:-1]
        lines.append(i)
    for i in range(noOfLinesBeforeData):
        del lines[0]

#ARRANGING DATA
for i in lines[:-1]: #[:-1] removes empty line
    currentLine = i.split()
    if len(currentLine) > 4: #if closed cycle
        start = int(currentLine[1])*12+int(currentLine[2])
        end = int(currentLine[4])*12+int(currentLine[5])
    else: #if open cycle
        start = int(currentLine[1])*12+int(currentLine[2])
        counter = 0
        sum = 0
        for j in data:
            sum += j[1]-j[0]
            counter += 1
        diff = int(sum/counter)
        end = start+diff
    if len(data) != 0:
        fullData.append([float(data[-1][0]), float(data[-1][1]), float(start-1)])
    data.append([start, end])
fullData.append([float(data[-1][0]), float(data[-1][1]), float(np.nan)])
startData = []
maxData = []
endData = []
for i in fullData:
    startData.append(i[0])
    maxData.append(i[1])
    endData.append(i[2])
fullData = [startData, maxData, endData]
#SAVING DATA
print('Exporting data into '+constants.RresultFileName)
pycdf.lib.set_backward(False)
saveFile = pycdf.CDF(constants.RresultFileName, '')
for i in range(3):
    saveFile[constants.labels[i]] = fullData[i]
saveFile.close()