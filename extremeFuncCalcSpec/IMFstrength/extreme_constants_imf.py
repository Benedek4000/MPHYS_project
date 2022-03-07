import os.path as path

lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'MFI/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeMFIstrength.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'BGSM']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minIMF', 'maxIMF']
dist_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['Minima', 'Maxima']]
ret_figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotDistFileName = path.join(lPath, 'extremeIMFstrength.png')
plotDistTitle=('EXTREME DISTRIBUTIONS OF IMF STRENGTH AT L1 FROM 1998 TO 2021\n'+
        '$\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$) for CDF')
plotRetFileName = path.join(lPath, 'extremeReturnIMFstrength.png')
plotRetTitle=('RETURN PERIODS OF IMF STRENGTH AT L1 FROM 1998 TO 2021\n'+
        '$\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and Return Level = $\^\u03BC$+$\^\u03C3$/$\^\u03BE$*((-log(1-1/R))^(-$\^\u03BE$)-1), where R is the Return Period in days')
init_guess = [[[], []], [[], []], [[], []]] #set up initial guesses for curve fitting
for solar_tag in range(3):
        for minmax in range(2):
                if minmax == 0:
                        init_guess[solar_tag][minmax] = [0.5, 0.2, 1]
                else:
                        init_guess[solar_tag][minmax] = [0.5, -0.2, 1]
