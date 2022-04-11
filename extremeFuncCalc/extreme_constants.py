import os.path as path
"""
#MFI
lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'MFI/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeMFI.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'BGSM']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
dist_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
ret_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotDistFileName = path.join(lPath, 'extremeMFI.png')
plotReturnFileName = path.join(lPath, 'extremeReturnMFI.png')
property='B'
units='nT'
plotDistTitle=('EXTREME DISTRIBUTIONS OF THE IMF AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$) for CDF')
plotRetTitle=('RETURN LEVELS AND RETURN PERIODS OF THE IMF AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and Return Level = $\^\u03BC$+$\^\u03C3$/$\^\u03BE$*((-log(1-1/R))^(-$\^\u03BE$)-1), where R is the Return Period in days')
init_guess = [[[[], []], [[], []], [[], []]], [[[], []], [[], []], [[], []]], [[[], []], [[], []], [[], []]]] #set up initial guesses for curve fitting
for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                init_guess[solar_tag][coordinate][minmax] = [0.5, 6, 1]

"""
#SWE
lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'SWE/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeSWE.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'V_GSM']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
dist_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
ret_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['X(GSM)', 'Y(GSM)', 'Z(GSM)'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotDistFileName = path.join(lPath, 'extremeSWE.png')
plotReturnFileName = path.join(lPath, 'extremeReturnSWE.png')
property='V'
units='km/s'
plotDistTitle=('EXTREME DISTRIBUTIONS OF SOLAR WIND VELOCITY AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$) for CDF')
plotRetTitle=('RETURN LEVELS AND RETURN PERIODS OF SOLAR WIND VELOCITY AT L1 FROM 1998 TO 2021\n'+
        'For figures of block minima, $\^z$ = -z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'For figures of block maxima, $\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and Return Level = $\^\u03BC$+$\^\u03C3$/$\^\u03BE$*((-log(1-1/R))^(-$\^\u03BE$)-1), where R is the Return Period in days')
init_guess = [[[[], []], [[], []], [[], []]], #set up initial guesses for curve fitting
        [[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]]]
for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                if coordinate == 0:
                        if minmax == 0:
                                init_guess[solar_tag][coordinate][minmax] = [0.5, 400, 50]
                        else:
                                init_guess[solar_tag][coordinate][minmax] = [0.5, -400, 100]
                else:
                        init_guess[solar_tag][coordinate][minmax] = [0.5, 6, 1]
#"""