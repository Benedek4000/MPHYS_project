import os.path as path

lPath = '/home/MPHYS/Data/'
RPath = path.join(lPath, 'Sunspots/')
RfileListName = path.join(RPath,'fileNames.txt')
RfileLengthName = path.join(RPath, 'fileLength.txt')
RresultFileName = path.join(lPath, 'solarActivity.cdf')
R_labels = ['R']
labels = ['periods'] #list of [start of period, start of next period, period type]
                    #start of period: year*12+month, included in period; start of next period: year*12+month, not included in period; period type: 'min' or 'int' or 'max'