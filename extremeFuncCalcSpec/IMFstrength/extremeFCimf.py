from cmath import inf
from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import genextreme as gev
import sympy as sym
from sympy.codegen.cfunctions import log
import os.path as path
import math
import extreme_constants_imf as constants


def returnLevel(p, parameters):

    returnL = [[[], []], [[], []], [[], []]]

    for solar_tag in range(3):
        for minmax in range(2):
            currentK=parameters[solar_tag][minmax][0]
            currentM=parameters[solar_tag][minmax][1]
            currentS=parameters[solar_tag][minmax][2]
            returnL[solar_tag][minmax] = [currentM+currentS/currentK*((-math.log(1-currentP))**(-currentK)-1) for currentP in p[solar_tag][minmax]]

    return returnL

def logData(data):
    
    for solar_tag in range(3):
        for minmax in range(2):
            data[solar_tag][minmax] = [math.log10(currentItem) for currentItem in data[solar_tag][minmax]]

    return data

def importFileNames(filePath, fileListName):

    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1]

def fixList(data): #deletes too high and too low values

    newData = []
    for i in range(len(data)):
        if (data[i] is None) == False:
            if (data[i] > -1e4 and data[i] < 1e4):# and (data[i] >= 1e-12 or data[i] <= -1e-12):
                newData.append(data[i])

    return newData

def getDayMinimumMaximum(fileName, orig_labels):

    Plist = []

    with pycdf.CDF(fileName) as currentFile:
        no_of_entries = len(currentFile[orig_labels[0]][:])
        currentEpoch = currentFile[orig_labels[0]][0]
        for i in range(no_of_entries):
            cE = currentFile[orig_labels[1]][i]
            Plist.append(math.sqrt(cE[0]**2+cE[1]**2+cE[2]**2))

    Plist = fixList(Plist)

    return [currentEpoch.year*12+currentEpoch.month, min(Plist, default=None), max(Plist, default=None)] #[month number, minP, maxP]

def epochToSolarActivity(data, sAFileName, solar_labels):

    #import solar periods
    with pycdf.CDF(sAFileName) as solarFile:
        solarPeriods = []
        for i in range(len(solarFile[solar_labels[0]][:])):
            solarPeriods.append([solarFile[solar_labels[0]][i], solarFile[solar_labels[1]][i], solarFile[solar_labels[2]][i]])

    #create epoch-lists for min, int and max
    minList = np.empty(shape=0)
    intList = np.empty(shape=0)
    maxList = np.empty(shape=0)
    for currentPeriod in solarPeriods:
        start = math.floor(currentPeriod[0])
        end = math.floor(currentPeriod[1])
        type = currentPeriod[2]
        monthsIncluded = np.arange(start, end, step=1)
        if type == 'min':
            for i in monthsIncluded:
                minList = np.append(minList, i)
        if type == 'int':
            for i in monthsIncluded:
                intList = np.append(intList, i)
        if type == 'max':
            for i in monthsIncluded:
                maxList = np.append(maxList, i)

    #replace month_number with solar_activity_tag
    for i in range(len(data)):
        if data[i][0] in minList:
            data[i][0] = 'min'
        elif data[i][0] in intList:
            data[i][0] = 'int'
        elif data[i][0] in maxList:
            data[i][0] = 'max'

    return data

def saveData(data, combinedFileName, labels):

    print('Exporting data into '+combinedFileName)
    pycdf.lib.set_backward(False)
    saveFile = pycdf.CDF(combinedFileName, '')
    for i in range(3):
        saveFile[labels[i]] = pd.DataFrame(data)[i].tolist()
    saveFile.close()

def getBlockMinimaMaxima(combinedFileName, filenames, orig_labels, solarActivityFileName, solar_labels, new_labels):

    if path.isfile(combinedFileName): #imports data from combined cdf if it exists
        with pycdf.CDF(combinedFileName) as dataFile:
            print('Importing Block Minima and Block Maxima from '+combinedFileName)
            data = []
            for i in range(len(dataFile[new_labels[0]][:])):
                currentLine = []
                for j in range(3):
                    currentLine.append(dataFile[new_labels[j]][i])
                data.append(currentLine)

    else:
        data = []
        for currentFileName in tqdm(filenames, desc='Retrieving Block Minima and Block Maxima'):
            data.append(getDayMinimumMaximum(currentFileName, orig_labels))
        #replace epoch with solar activity tag ('min', 'int' or 'max')
        data = epochToSolarActivity(data, solarActivityFileName, solar_labels)
        saveData(data, combinedFileName, new_labels)

    return data

def distributeData(data): #output has these indexes: processedData[solar_tag][minima/maxima]
    #solar_tag: 'min' -> 0, 'int' -> 1, 'max' -> 2
    #minima/maxima: minima -> 0, maxima -> 1

    processedData = [[[], []], [[], []], [[], []]]

    for currentLine in data:
        if currentLine[0] == 'min':
            solar_tag = 0
        elif currentLine[0] == 'int':
            solar_tag = 1
        elif currentLine[0] == 'max':
            solar_tag = 2
        for minmax in range(2):
            processedData[solar_tag][minmax].append(currentLine[minmax+1])

    #sort data
    for solar_tag in range(3):
        for minmax in range(2):
                processedData[solar_tag][minmax] = sorted(fixList(processedData[solar_tag][minmax]))

    return processedData

def generateG(processedZ):

    G = [[[], []], [[], []], [[], []]]
    z = [[[], []], [[], []], [[], []]]

    for solar_tag in range(3):
        for minmax in range(2):
            currentLineZ = []
            currentLineG = []

            #remove infs and NaNs and flipping sign of z for minima
            for i in processedZ[solar_tag][minmax]:
                if i != inf and math.isnan(i) == False:
                    currentLineZ.append(i)

            for i in currentLineZ:
                if minmax == 0: #if list of minima
                    currentLineG.append(sum(i >= j for j in processedZ[solar_tag][minmax]))
                if minmax == 1: #if list of maxima
                    currentLineG.append(sum(i >= j for j in processedZ[solar_tag][minmax]))
                #currentLineG.append(sum(i >= j for j in processedZ[solar_tag][minmax]))

            #normalise G
            norm_factor = max(currentLineG)
            z[solar_tag][minmax] = currentLineZ
            G[solar_tag][minmax] = [currentElement/norm_factor for currentElement in currentLineG]
            #G[solar_tag][minmax] = currentLineG

    return z, G

def flipZ(processedZ):

    z = [[[], []], [[], []], [[], []]]

    for solar_tag in range(3):
        for minmax in range(2):
            if minmax == 0:
                z[solar_tag][minmax] = [-currentElement for currentElement in processedZ[solar_tag][minmax]]
            else :
                z[solar_tag][minmax] = processedZ[solar_tag][minmax]

    return z

def flipParam(param, minmax):

    """if minmax == 0:
        param = -param"""
    
    return param

def fit_curves(z, G, init):

    parameters = [[[], []], [[], []], [[], []]]

    err_parameters = [[[], []], [[], []], [[], []]]

    var_covar = [[[], []], [[], []], [[], []]]

    for solar_tag in trange(3, desc='Fitting Curves', position=0):
        for minmax in trange(2, desc='Fitting Curves', position=1, leave=False):

            popt, pcov = curve_fit(gev.cdf, z[solar_tag][minmax], G[solar_tag][minmax], maxfev=500000, p0 = init[solar_tag][minmax])
            xi, mu, sigma = popt
            err_xi, err_mu, err_sigma = math.sqrt(pcov[0,0]), math.sqrt(pcov[1,1]), math.sqrt(pcov[2,2])
            parameters[solar_tag][minmax] = [-xi, mu, sigma]
            err_parameters[solar_tag][minmax] = [err_xi, err_mu, err_sigma]
            var_covar[solar_tag][minmax] = pcov

    return parameters, err_parameters, var_covar

def plotData(z, G, parameters, err_parameters, figure_labels, save, plotFileName, plotTitle):

    fig, axs = plt.subplots(nrows=6, ncols=2)
    fig.suptitle(plotTitle, fontsize=35, y=1)

    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):

        solar_tag = math.floor(i/4)
        cdfpdf = math.floor((i-solar_tag*4)/2)
        minmax = math.floor(i-solar_tag*4-cdfpdf*2)

        subplot_title = figure_labels[1][cdfpdf]+' for '+figure_labels[0][solar_tag]+' '+figure_labels[2][minmax]
        ax.title.set_text(subplot_title)
        ax.set(xlabel='z (nT)', ylabel='G(z)')

        #flippedZ = flipZ(z)
        flippedZ = z

        if cdfpdf == 0: #CDF
            ax.scatter(z[solar_tag][minmax], G[solar_tag][minmax], s=1)
            CDF = gev.cdf(flippedZ[solar_tag][minmax], -parameters[solar_tag][minmax][0], 
                parameters[solar_tag][minmax][1], parameters[solar_tag][minmax][2])
            ax.plot(z[solar_tag][minmax], CDF, color='r')
        else: #PDF
            PDF = gev.pdf(flippedZ[solar_tag][minmax], -parameters[solar_tag][minmax][0], 
                parameters[solar_tag][minmax][1], parameters[solar_tag][minmax][2])
            ax.plot(z[solar_tag][minmax], PDF, color='r')

        ax.plot([], [], ' ', label='\u03BE = '+'{0:.3f}'.format(parameters[solar_tag][minmax][0])+r'$\pm$'+'{0:.3f}'.format(err_parameters[solar_tag][minmax][0]))
        ax.plot([], [], ' ', label='\u03BC = '+'{0:.3f}'.format(parameters[solar_tag][minmax][1])+r'$\pm$'+'{0:.3f}'.format(err_parameters[solar_tag][minmax][1]))
        ax.plot([], [], ' ', label='\u03C3 = '+'{0:.3f}'.format(parameters[solar_tag][minmax][2])+r'$\pm$'+'{0:.3f}'.format(err_parameters[solar_tag][minmax][2]))

        if cdfpdf == 0:
            ax.legend(loc='lower right', prop={'size': 25})
        else:
            ax.legend(loc='upper right', prop={'size': 25})

    fig.subplots_adjust(wspace=0.25)
    if save:
        fig.set_size_inches(40, 30)
        plt.savefig(plotFileName, bbox_inches='tight', dpi=100)
    else:
        plt.show()

    return None

def generateReturnData(z, parameters, var_covar):

    R = [[[], []], [[], []], [[], []]]

    P = [[[], []], [[], []], [[], []]]

    err_RL = [[[], []], [[], []], [[], []]]

    p, k, m, s = sym.symbols('p k m s')
    z=m-s/k*(1-(-log(1-p))**(-k))
    deltaZ=[sym.diff(z, k), sym.diff(z, m), sym.diff(z, s)]

    for solar_tag in range(3):
        for minmax in range(2):
            R[solar_tag][minmax] = [10**i for i in np.linspace(-1, 3, num=101)]
            P[solar_tag][minmax] = [1/(currentR*365) for currentR in R[solar_tag][minmax]]
            currentK = parameters[solar_tag][minmax][0]
            currentM = flipParam(parameters[solar_tag][minmax][1], minmax)
            currentS = parameters[solar_tag][minmax][2]
            currentDZ=[i.subs(k, currentK).subs(m, currentM).subs(s, currentS) for i in deltaZ]
            err_RL[solar_tag][minmax] = [math.sqrt(np.matmul(np.matmul([i.subs(p, currentP).evalf() for i in currentDZ], var_covar[solar_tag][minmax]), [i.subs(p, currentP).evalf() for i in currentDZ])) for currentP in P[solar_tag][minmax]]

    return logData(R), returnLevel(P, parameters), err_RL

def plotReturnData(R, returnL, err_RL, figure_labels, save, plotFileName, plotTitle):

    fig, axs = plt.subplots(nrows=3, ncols=2)
    fig.suptitle(plotTitle, fontsize=35, y=1)

    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):

        solar_tag = math.floor(i/2)
        minmax = math.floor(i-solar_tag*2)

        subplot_title = 'Return Levels for '+figure_labels[0][solar_tag]+' '+figure_labels[1][minmax]
        ax.title.set_text(subplot_title)
        ax.set(xlabel='log10 Return Period (years)', ylabel='Return Level (nT)')

        ax.plot(R[solar_tag][minmax], returnL[solar_tag][minmax], color='b')
        regTop=[returnL[solar_tag][minmax][i]+err_RL[solar_tag][minmax][i] for i in range(len(err_RL[solar_tag][minmax]))]
        regBot=[returnL[solar_tag][minmax][i]-err_RL[solar_tag][minmax][i] for i in range(len(err_RL[solar_tag][minmax]))]
        ax.fill_between(x=R[solar_tag][minmax], y1=regBot, y2=regTop, color='r', alpha=0.2)
        ax.ticklabel_format(useOffset=False, style='plain')

    fig.subplots_adjust(wspace=0.25)
    if save:
        fig.set_size_inches(40, 30)
        plt.savefig(plotFileName, bbox_inches='tight', dpi=100)
    else:
        plt.show()

    return None

def main(fileListName, filePath, combinedFileName, solarActivityFileName, orig_labels, solar_labels, new_labels, dist_figure_labels, ret_figure_labels, save, plotDistFileName, plotRetFileName, plotDistTitle, plotRetTitle, init):
    #get block minima and maxima. process and save data, if it can't be loaded.
    #data=[solar_activity_tag, minX, minY, minZ, maxX, maxY, maxZ]. solar_activity_tag is either 'min', 'int' or 'max'
    data = getBlockMinimaMaxima(combinedFileName, importFileNames(filePath, fileListName), orig_labels, solarActivityFileName, solar_labels, new_labels)
    processedZ = distributeData(data)
    processedZ, processedG = generateG(processedZ)
    parameters, err_parameters, var_covar = fit_curves(processedZ, processedG, init)
    plotData(processedZ, processedG, parameters, err_parameters, dist_figure_labels, save, plotDistFileName, plotDistTitle)
    retR, retL, err_RL = generateReturnData(processedZ, parameters, var_covar)
    plotReturnData(retR, retL, err_RL, ret_figure_labels, save, plotRetFileName, plotRetTitle)
    

main(constants.fileListName, constants.filePath, constants.combinedFileName, constants.solarActivityFileName, constants.orig_labels, constants.solar_labels, constants.new_labels, 
    constants.dist_figure_labels, constants.ret_figure_labels, constants.save, constants.plotDistFileName, constants.plotRetFileName, constants.plotDistTitle, constants.plotRetTitle, constants.init_guess)