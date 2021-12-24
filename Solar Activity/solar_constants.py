import os.path as path

lPath = '/home/MPHYS/Data/'
RPath = path.join(lPath, 'Sunspots/')
RdatafileName = path.join(RPath, 'TableCyclesMiMa.txt')
RresultFileName = path.join(lPath, 'solarActivity.cdf')
labels = ['start', 'max', 'end'] #list of [start of cycle, maximum of cycle, end of cycle], number refers to year*12+month