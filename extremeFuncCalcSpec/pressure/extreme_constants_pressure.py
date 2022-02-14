import os.path as path

#SWE
m_p=1.67e-27 #proton mass

lPath = '/home/MPHYS/Data/'
filePath = path.join(lPath, 'SWE/')
fileListName = path.join(filePath,'fileNames.txt')
combinedFileName = path.join(lPath, 'combinedExtremeSWEpressure.cdf')
solarActivityFileName = path.join(lPath, 'solarActivity.cdf')
orig_labels = ['Epoch', 'Np', 'Vp']
solar_labels = ['start', 'end', 'type']
new_labels = ['solar_tag', 'minP', 'maxP']
figure_labels = [['Minimum', 'Intermediate', 'Maximum'], ['CDF', 'PDF'], ['Minima', 'Maxima']]
save = True #True to save the plot, False to show the plot
plotFileName = path.join(lPath, 'extremeP.png')
plotTitle=('EXTREME DISTRIBUTIONS OF SOLAR WIND RAM PRESSURE AT L1 FROM 1998 TO 2021\n'+
        '$\^z$ = z, $\^\u03BE$ = \u03BE, $\^\u03BC$ = \u03BC, $\^\u03C3$ = \u03C3\n'+
        'and G(t) = exp(-t), where t(z, $\^\u03BE$, $\^\u03BC$, $\^\u03C3$) = (1+$\^\u03BE$(($\^z$-$\^\u03BC$)/$\^\u03C3$))^(-1/$\^\u03BE$) for CDF')
init_guess = [[[], []], [[], []], [[], []]] #set up initial guesses for curve fitting
for solar_tag in range(3):
        for minmax in range(2):
                if minmax == 0:
                        init_guess[solar_tag][minmax] = [0.5, 0.2, 1]
                else:
                        init_guess[solar_tag][minmax] = [0.5, -0.2, 1]
