from spacepy import pycdf
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import os.path as path
import math
import extreme_constants as constants

def GEV_CDF(z, xi, mu, sigma):
    G = np.array([])
    t=0
    for i in z:
        if xi==0:
            t = math.e**(-(i-mu)/sigma)
        else:
            t = (1+xi*(i-mu)/sigma)**(-1/xi)
        newG = math.e**(-t)
        G = np.append(G, newG)
    return G

def GEV_PDF(z, xi, mu, sigma):
    G = np.array([])
    t=0
    for i in z:
        if xi==0:
            t = math.e**(-(i-mu)/sigma)
        else:
            t = (1+xi*(i-mu)/sigma)**(-1/xi)
        newG = 1/sigma*t**(xi+1)*math.e**(-t)
        G = np.append(G, newG)
    return G

def importFileNames(filePath, fileListName):
    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1]

def fixList(data): #replaces too high and too low values with None
    newData = []
    for i in range(len(data)):
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
                processedData[solar_tag][coordinate][minmax] = sorted(processedData[solar_tag][coordinate][minmax])
    return processedData

def generateG(processedZ):
    G = [[[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]], 
        [[[], []], [[], []], [[], []]]]
    for solar_tag in range(3):
        for coordinate in range(3):
            for minmax in range(2):
                currentLine = []
                for i in processedZ[solar_tag][coordinate][minmax]:
                    if minmax == 0: #if list of minima
                        currentLine.append(sum(i >= j for j in processedZ[solar_tag][coordinate][minmax]))
                    if minmax == 1: #if list of maxima
                        currentLine.append(sum(i <= j for j in processedZ[solar_tag][coordinate][minmax]))
                G[solar_tag][coordinate][minmax] = currentLine
    return G

def main(fileListName, filePath, combinedFileName, solarActivityFileName, orig_labels, solar_labels, new_labels, save, plotFileName):
    #get block minima and maxima. process and save data, if it can't be loaded. data=[solar_activity_tag, minX, minY, minZ, maxX, maxY, maxZ]. solar_activity_tag is either 'min', 'int' or 'max'
    data = getBlockMinimaMaxima(combinedFileName, importFileNames(filePath, fileListName), orig_labels, solarActivityFileName, solar_labels, new_labels)
    processedZ = distributeData(data)
    processedG = generateG(processedZ)
    
    fig = plt.figure()

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.scatter(processedZ[0][0][0], processedG[0][0][0])
    ax2.scatter(processedZ[0][0][1], processedG[0][0][1])

    print(processedZ[0][0][0])
    print(processedG[0][0][0])
    print('X')
    print(processedZ[0][0][1])
    print(processedG[0][0][1])

    plt.show()

main(constants.fileListName, constants.filePath, constants.combinedFileName, constants.solarActivityFileName, constants.orig_labels, constants.solar_labels, constants.new_labels, constants.save, constants.plotFileName)