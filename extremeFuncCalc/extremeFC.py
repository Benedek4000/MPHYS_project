from cmath import inf
from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import genextreme as gev
import os.path as path
import math
import extreme_constants as constants

def returnLevel(z, parameters):

    returnL = [[[[], []], [[], []], [[], []]], 
                [[[], []], [[], []], [[], []]], 
                [[[], []], [[], []], [[], []]]]

    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                currentK=parameters[solar_tag][coordinate][minmax][0]
                currentM=flipParam(parameters[solar_tag][coordinate][minmax][1], minmax)
                currentS=parameters[solar_tag][coordinate][minmax][2]
                returnL[solar_tag][coordinate][minmax] = [1/(365*(1-CDF)) for CDF in gev.cdf(flipZ(z)[solar_tag][coordinate][minmax], c=currentK, loc=currentM, scale=currentS)]

    return returnL

def logData(data):
    
    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                data[solar_tag][coordinate][minmax] = [math.log10(currentItem) for currentItem in data[solar_tag][coordinate][minmax]]

    return data

def importFileNames(filePath, fileListName):

    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1]

def fixList(data): #deletes too high and too low values

    newData = []
    for i in range(len(data)):
        if (data[i] is None) == False:
            if (data[i] > -1e5 and data[i] < 1e5) and (data[i] != 0):
                newData.append(data[i])

    return newData

def getDayMinimumMaximum(fileName, orig_labels):

    Xlist = []
    Ylist = []
    Zlist = []

    with pycdf.CDF(fileName) as currentFile:
        no_of_entries = len(currentFile[orig_labels[0]][:])
        currentEpoch = currentFile[orig_labels[0]][0]
        for i in range(no_of_entries):
            currentValue = currentFile[orig_labels[1]][i]
            Xlist.append(currentValue[0])
            Ylist.append(currentValue[1])
            Zlist.append(currentValue[2])

    Xlist = fixList(Xlist)
    Ylist = fixList(Ylist)
    Zlist = fixList(Zlist)

    return [currentEpoch.year*12+currentEpoch.month, min(Xlist, default=None), min(Ylist, default=None), min(Zlist, default=None), max(Xlist, default=None), max(Ylist, default=None), max(Zlist, default=None)] #[month number, minX, minY, minZ, maxX, maxY, maxZ]

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
    for i in range(7):
        saveFile[labels[i]] = pd.DataFrame(data)[i].tolist()
    saveFile.close()

def getBlockMinimaMaxima(combinedFileName, filenames, orig_labels, solarActivityFileName, solar_labels, new_labels):

    if path.isfile(combinedFileName): #imports data from combined cdf if it exists
        with pycdf.CDF(combinedFileName) as dataFile:
            print('Importing Block Minima and Block Maxima from '+combinedFileName)
            data = []
            for i in range(len(dataFile[new_labels[0]][:])):
                currentLine = []
                for j in range(7):
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

def distributeData(data): #output has these indexes: processedData[solar_tag][coordinate][minima/maxima]
    #solar_tag: 'min' -> 0, 'int' -> 1, 'max' -> 2
    #coordinate: X -> 0, Y -> 1, Z -> 2
    #minima/maxima: minima -> 0, maxima -> 1

    processedData = [[[[], []], [[], []], [[], []]], 
                    [[[], []], [[], []], [[], []]], 
                    [[[], []], [[], []], [[], []]]]

    for currentLine in data:
        if currentLine[0] == 'min':
            solar_tag = 0
        elif currentLine[0] == 'int':
            solar_tag = 1
        elif currentLine[0] == 'max':
            solar_tag = 2
        for coordinate in range(3):
            for minmax in range(2):
                processedData[solar_tag][coordinate][minmax].append(currentLine[3*minmax+coordinate+1])

    #sort data
    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                processedData[solar_tag][coordinate][minmax] = sorted(fixList(processedData[solar_tag][coordinate][minmax]))

    return processedData

def generateG(processedZ):

    G = [[[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]]]
    z = [[[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]]]

    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                currentLineZ = []
                currentLineG = []

                #remove infs and NaNs and flipping sign of z for minima
                for i in processedZ[solar_tag][coordinate][minmax]:
                    if i != inf and math.isnan(i) == False:
                        currentLineZ.append(i)

                for i in currentLineZ:
                    if minmax == 0: #if list of minima
                        currentLineG.append(sum(i <= j for j in processedZ[solar_tag][coordinate][minmax]))
                    if minmax == 1: #if list of maxima
                        currentLineG.append(sum(i >= j for j in processedZ[solar_tag][coordinate][minmax]))
                    #currentLineG.append(sum(i >= j for j in processedZ[solar_tag][coordinate][minmax]))

                #normalise G
                norm_factor = max(currentLineG)
                z[solar_tag][coordinate][minmax] = currentLineZ
                G[solar_tag][coordinate][minmax] = [currentElement/norm_factor for currentElement in currentLineG]
                #G[solar_tag][coordinate][minmax] = currentLineG

    return z, G

def flipZ(processedZ):

    z = [[[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]]]

    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                if minmax == 0:
                    z[solar_tag][coordinate][minmax] = [-currentElement for currentElement in processedZ[solar_tag][coordinate][minmax]]
                else :
                    z[solar_tag][coordinate][minmax] = processedZ[solar_tag][coordinate][minmax]

    return z

def flipParam(param, minmax):

    if minmax == 0:
        param = -param
    
    return param

def fit_curves(z, G, init):

    parameters = [[[[], []], [[], []], [[], []]], 
                [[[], []], [[], []], [[], []]], 
                [[[], []], [[], []], [[], []]]]

    for solar_tag in trange(3, desc='Fitting Curves', position=0):
        for coordinate in trange(3, desc='Fitting Curves', position=1, leave=False):
            for minmax in trange(2, desc='Fitting Curves', position=2, leave=False):

                popt, pcov = curve_fit(gev.cdf, z[solar_tag][coordinate][minmax], G[solar_tag][coordinate][minmax], maxfev=500000, p0 = init[solar_tag][coordinate][minmax])
                xi, mu, sigma = popt
                if minmax == 1:
                    parameters[solar_tag][coordinate][minmax] = [xi, mu, sigma]
                else:
                    parameters[solar_tag][coordinate][minmax] = [xi, -mu, sigma]
                
    return parameters

def plotDistData(z, G, parameters, figure_labels, save, plotFileName, plotTitle):

    fig, axs = plt.subplots(nrows=6, ncols=6)
    fig.suptitle(plotTitle, fontsize=35, y=1)

    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):

        solar_tag = math.floor(i/12)
        cdfpdf = math.floor((i-solar_tag*12)/6)
        coordinate = math.floor((i-solar_tag*12-cdfpdf*6)/2)
        minmax = math.floor(i-solar_tag*12-cdfpdf*6-coordinate*2)

        subplot_title = figure_labels[1][cdfpdf]+' for '+figure_labels[0][solar_tag]+' '+figure_labels[2][coordinate]+' '+figure_labels[3][minmax]
        ax.title.set_text(subplot_title)
        ax.set(xlabel='z', ylabel='G(z)')

        flippedZ = flipZ(z)

        if cdfpdf == 0: #CDF
            ax.scatter(z[solar_tag][coordinate][minmax], G[solar_tag][coordinate][minmax], s=1)
            CDF = gev.cdf(flippedZ[solar_tag][coordinate][minmax], parameters[solar_tag][coordinate][minmax][0], 
                flipParam(parameters[solar_tag][coordinate][minmax][1], minmax), parameters[solar_tag][coordinate][minmax][2])
            ax.plot(z[solar_tag][coordinate][minmax], CDF, color='r')
        else: #PDF
            PDF = gev.pdf(flippedZ[solar_tag][coordinate][minmax], parameters[solar_tag][coordinate][minmax][0], 
                flipParam(parameters[solar_tag][coordinate][minmax][1], minmax), parameters[solar_tag][coordinate][minmax][2])
            ax.plot(z[solar_tag][coordinate][minmax], PDF, color='r')

        ax.plot([], [], ' ', label='\u03BE = '+'{0:.3f}'.format(parameters[solar_tag][coordinate][minmax][0]))
        ax.plot([], [], ' ', label='\u03BC = '+'{0:.3f}'.format(flipParam(parameters[solar_tag][coordinate][minmax][1], minmax)))
        ax.plot([], [], ' ', label='\u03C3 = '+'{0:.3f}'.format(parameters[solar_tag][coordinate][minmax][2]))

        legendloc=''
        if cdfpdf == 0:
            legendloc = legendloc + 'lower '
        else:
            legendloc = legendloc + 'upper '
        if minmax == 0:
            legendloc = legendloc + 'left'
        else:
            legendloc = legendloc + 'right'
        if constants.filePath==path.join('/home/MPHYS/Data/', 'SWE/'):
            if coordinate == 0 and (cdfpdf == 1 or minmax == 1):
                legendloc = 'upper left'
        ax.legend(loc=legendloc, prop={'size': 10})


    fig.subplots_adjust(wspace=0.25)
    if save:
        fig.set_size_inches(40, 30)
        plt.savefig(plotFileName, bbox_inches='tight', dpi=100)
    else:
        plt.show()

    return None

def generateReturnData(z, parameters):

    dispZ = [[[[], []], [[], []], [[], []]], 
            [[[], []], [[], []], [[], []]], 
            [[[], []], [[], []], [[], []]]]

    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                dispZ[solar_tag][coordinate][minmax] = np.linspace(min(z[solar_tag][coordinate][minmax]), 2.5*max(z[solar_tag][coordinate][minmax])-1.5*min(z[solar_tag][coordinate][minmax]), 101)

    return dispZ, logData(returnLevel(flipZ(dispZ), parameters))

def plotReturnData(z, returnL, figure_labels, save, plotFileName, plotTitle):

    fig, axs = plt.subplots(nrows=3, ncols=6)
    fig.suptitle(plotTitle, fontsize=35, y=1)

    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):

        solar_tag = math.floor(i/6)
        coordinate = math.floor((i-solar_tag*6)/2)
        minmax = math.floor(i-solar_tag*6-coordinate*2)

        subplot_title = 'Return Periods for '+figure_labels[0][solar_tag]+' '+figure_labels[1][coordinate]+' '+figure_labels[2][minmax]
        ax.title.set_text(subplot_title)
        ax.set(xlabel='z', ylabel='log10 Return Period (years)')

        flippedZ = flipZ(z)

        ax.plot(flippedZ[solar_tag][coordinate][minmax], returnL[solar_tag][coordinate][minmax], color='r')
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
    parameters = fit_curves(flipZ(processedZ), processedG, init)
    plotDistData(processedZ, processedG, parameters, dist_figure_labels, save, plotDistFileName, plotDistTitle)
    retZ, retL = generateReturnData(flipZ(processedZ), parameters)
    plotReturnData(retZ, retL, ret_figure_labels, save, plotRetFileName, plotRetTitle)
    

main(constants.fileListName, constants.filePath, constants.combinedFileName, constants.solarActivityFileName, constants.orig_labels, constants.solar_labels, constants.new_labels, 
    constants.dist_figure_labels, constants.ret_figure_labels, constants.save, constants.plotDistFileName, constants.plotReturnFileName, constants.plotDistTitle, constants.plotRetTitle, constants.init_guess)