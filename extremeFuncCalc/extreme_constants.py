import os.path as path

#MFI
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
plotTitle=('EXTREME DISTRIBUTIONS OF THE IMF AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$)')

"""
#SWE
lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'SWE/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeSWE.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'V_GSM', 'label_V_GSM']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotFileName = path.join(lPath, 'extremeSWE.png')
plotTitle=('EXTREME DISTRIBUTIONS OF SOLAR WIND VELOCITY AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$)')
"""