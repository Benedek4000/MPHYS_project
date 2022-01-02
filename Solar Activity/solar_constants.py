import os.path as path

lPath = '/home/MPHYS/Data/'
RPath = path.join(lPath, 'Sunspots/')
RdatafileName = path.join(RPath, 'TableCyclesMiMa.txt')
RresultFileName = path.join(lPath, 'solarActivity.cdf')
labels = ['start', 'end', 'type'] #list of [start of period, maximum of period, type of period (min, int or max)], number refers to year*12+month