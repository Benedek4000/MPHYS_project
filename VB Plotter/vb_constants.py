import os.path as path

lPath = '/home/MPHYS/Data/'
MFIPath = path.join(lPath, 'MFI/')
MFIfileListName = path.join(MFIPath,'fileNames.txt')
MFIfileLengthName = path.join(MFIPath, 'fileLength.txt')
MFI_labels = ['BGSM', 'Epoch', 'label_bgsm']

SWEPath = path.join(lPath, 'SWE/')
SWEfileListName = path.join(SWEPath,'fileNames.txt')
#SWEfileLengthName = path.join(SWEPath, 'fileLength.txt')
SWE_labels = ['V_GSM', 'Epoch', 'label_V_GSM']

VBcombinedFileName = path.join(lPath, 'combinedVB.cdf')
VBmemmapFileName = path.join(lPath, 'data.dat')

labels = ['Epoch, ''BGSM_X', 'BGSM_Y', 'BGSM_Z', 'V_GSM_X', 'V_GSM_Y', 'V_GSM_Z', 'labels']
save = False #True to save the plot, False to show the plot
histogramFileName = path.join(lPath, 'VBhistogramFull.png')