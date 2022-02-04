import os.path as path

lPath = '/home/MPHYS/Data/'
combinedFileName = path.join(lPath, 'combinedMFI.cdf')
labels = ['BGSM_structure', 'BGSM_no_of_entries', 'BGSM_X_min', 'BGSM_Y_min', 'BGSM_Z_min', 'BGSM_X_int', 'BGSM_Y_int', 'BGSM_Z_int', 'BGSM_X_max', 'BGSM_Y_max', 'BGSM_Z_max', 'labels', 'mean', 'std_dev']
sigmaCutoff=3
save = False #True to save the plot, False to show the plot
plotFileName = path.join(lPath, 'extremePlotFull.png')