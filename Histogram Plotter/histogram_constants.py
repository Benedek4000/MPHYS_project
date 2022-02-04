import os.path as path

lPath = '/home/MPHYS/Data/'
MFIPath = path.join(lPath, 'SWE/')
MFIfileListName = path.join(MFIPath,'fileNames.txt')
MFIfileLengthName = path.join(MFIPath, 'fileLength.txt')
MFIcombinedFileName = path.join(lPath, 'combinedSWE.cdf')
MFImemmapFileName = path.join(MFIPath, 'data.dat')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
MFI_labels = ['V_GSM', 'Epoch', 'label_V_GSM']
labels = ['VGSM_structure', 'VGSM_no_of_entries', 'VGSM_X_min', 'VGSM_Y_min', 'VGSM_Z_min', 'VGSM_X_int', 'VGSM_Y_int', 'VGSM_Z_int', 'VGSM_X_max', 'VGSM_Y_max', 'VGSM_Z_max', 'labels', 'mean', 'std_dev']
#bin_structure = [-50, 0.2, 500] #[bin1 lower limit, bin width, number of bins] FOR MFI
bin_structure = [-1200, 1, 1600] #[bin1 lower limit, bin width, number of bins] FOR SWE
save = False #True to save the plot, False to show the plot
histogramFileName = path.join(lPath, 'histogramFull.png')