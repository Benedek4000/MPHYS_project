import os.path as path

lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'MFI/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeMFI.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'BGSM', 'label_bgsm']
solar_labels = ['start', 'end', 'type']
#MODIFY new_labels
new_labels = ['solar_tag', 'minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
save = False #True to save the plot, False to show the plot
plotFileName = path.join(lPath, 'extremeMFI.png')