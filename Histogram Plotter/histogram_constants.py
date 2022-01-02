import os.path as path

lPath = '/home/MPHYS/Data/'
MFIPath = path.join(lPath, 'MFI/')
MFIfileListName = path.join(MFIPath,'fileNames.txt')
MFIfileLengthName = path.join(MFIPath, 'fileLength.txt')
MFIcombinedFileName = path.join(lPath, 'combined.cdf')
MFImemmapFileName = path.join(MFIPath, 'data.dat')
MFI_labels = ['BGSM', 'Epoch', 'label_bgsm']
labels = ['BGSM_structure', 'BGSM_no_of_entries', 'BGSM_X_min', 'BGSM_X_int', 'BGSM_X_max', 'BGSM_Y_min', 'BGSM_Y_int','BGSM_Y_max', 'BGSM_Z_min', 'BGSM_Z_int', 'BGSM_Z_max', 'labels', 'mean', 'std_dev']
bin_structure = [-50, 0.2, 500] #[bin1 lower limit, bin width, number of bins]
save = False #True to save the plot, False to show the plot
histogramFileName = path.join(lPath, 'histogramFull.png')