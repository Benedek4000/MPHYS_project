import os.path as path

lPath = '/home/MPHYS/Data/'
MFIPath = path.join(lPath, 'MFI/')
MFIfileListName = path.join(MFIPath,'fileNames.txt')
MFIfileLengthName = path.join(MFIPath, 'fileLength.txt')
MFIcombinedFileName = path.join(lPath, 'combined.cdf')
MFImemmapFileName = path.join(MFIPath, 'data.dat')
MFI_labels = ['BGSM', 'label_bgsm']
labels = ['BGSM_structure', 'BGSM_no_of_entries', 'BGSM_X', 'BGSM_Y', 'BGSM_Z', 'labels', 'mean', 'std_dev']
bin_structure = [-50, 0.2, 500] #[bin1 lower limit, bin width, number of bins]
save = False #True to save the plot, False to show the plot
histogramFileName = path.join(lPath, 'histogramFull.png')