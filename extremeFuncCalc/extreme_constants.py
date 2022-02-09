import os.path as path

lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'MFI/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeMFI.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'BGSM', 'label_bgsm']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotFileName = path.join(lPath, 'extremeMFI.png')