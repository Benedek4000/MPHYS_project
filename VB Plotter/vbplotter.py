from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import os.path as path
import os
import math
import vb_constants as constants

#create memmap array for [epoch,bgsm,vgsm data]
#import bgsm + epoch into array
#import vgsm into separate array
#match vgsm and bgsm data in memmap array
#plot graph
#maybe use tensorflow to determine relationship???

#IMPORTING CONSTANTS
MFIfileLengthName = constants.MFIfileLengthName
MFIPath = constants.MFIPath
original_MFI_labels = constants.MFI_labels
MFIfileListName = constants.MFIfileListName

SWEPath = constants.SWEPath
original_SWE_labels = constants.SWE_labels
SWEfileListName = constants.SWEfileListName

VBmemmapFileName = constants.VBmemmapFileName

def setupNumpyArray(fileLengthName, filenames, original_labels, memmapName): #setting up numpy array
    if path.isfile(fileLengthName):
        with open(fileLengthName, 'r') as f:
            dataLength = int(f.read())
        print('Array has been set up.')
    else:
        dataLength = sum(len(pycdf.CDF(i)[original_labels[0]][:]) for i in tqdm(filenames, desc='Setting Up Numpy Array'))
        with open(fileLengthName, 'w') as f:
            f.write(str(dataLength))
    return np.memmap(memmapName, dtype=float, mode='w+', shape=(dataLength,7)) #[epoch, bgsm[x,y,z], v_gsm[x,y,z]]

def importFilenames(filePath, fileListName): #importing filenames
    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1] #[:-1]s remove the \n from the end of each line and remove the txt filename from the list respectively

def importData(data, MFIfilenames, SWEfilenames, original_MFI_lables, original_SWE_lables):
    counter = 0
    for currentFileName in tqdm(MFIfilenames, desc='Importing MFI Data'):
        with pycdf.CDF(currentFileName) as currentFile:
            saved_counter = counter
            for currentEpoch in currentFile[original_MFI_lables[1]][:]:
                data[counter][0] = 1000000*currentEpoch.year+10000*currentEpoch.month+100*currentEpoch.day+currentEpoch.hour
                counter += 1
            for currentLine in currentFile[original_MFI_labels[0]][:]:
                data[saved_counter][1] = currentLine[0]
                data[saved_counter][2] = currentLine[1]
                data[saved_counter][3] = currentLine[2]
                saved_counter += 1
    swedata = {}
    for currentFileName in tqdm(SWEfilenames, desc='Importing SWE Data'):
        with pycdf.CDF(currentFileName) as currentFile:
            for i in range(len(currentFile[original_SWE_labels[1]][:])):
                currentEpoch = currentFile[original_SWE_labels[1]][i]
                currentLine = currentFile[original_SWE_labels[0]][i]
                swedata[str(1000000*currentEpoch.year+10000*currentEpoch.month+100*currentEpoch.day+currentEpoch.hour)] = [currentLine[0], currentLine[1], currentLine[2]]
            for index, currentLine in enumerate(data):
                if str(currentLine[0])[:10] in swedata.keys():
                    key=str(currentLine[0])[:10]
                    data[index][4] = swedata[key][0]
                    data[index][5] = swedata[key][1]
                    data[index][6] = swedata[key][2]
                else:
                    data[index][4] = None
                    data[index][5] = None
                    data[index][6] = None
    return data

def fixData(data): #replaces too high and too low values with None
    for i in trange(len(data), desc='Invalidating Erroneous Data', miniters=100000):
        for j in range(1, len(data[i]), 1):
            if (data[i][j] < -1e5 or data[i][j] > 1e5) or (data[i][j] == 0):
                data[i][j] = None
    return data

def plotData(data, save, histogramFileName):
    fig, axs = plt.subplots(ncols=3)
    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):
        xaxis=[]
        yaxis=[]
        for j in data:
            xaxis.append(j[i+4])
            yaxis.append(j[i+1])
        ax.scatter(xaxis,yaxis, s=5)
    if save:
        plt.savefig(histogramFileName, dpi=100)
    else:
        plt.show()
    return None

def main():
    MFIfilenames = importFilenames(MFIPath, MFIfileListName)
    SWEfilenames = importFilenames(SWEPath, SWEfileListName)
    data = setupNumpyArray(MFIfileLengthName, MFIfilenames, original_MFI_labels, VBmemmapFileName)
    data = importData(data, MFIfilenames, SWEfilenames, original_MFI_labels, original_SWE_labels)
    data = fixData(data)
    """for i in data:
        currentline=''
        for j in i:
            currentline=currentline+str(round(j,2))+';'
        print(currentline)"""
    plotData(data, constants.save, constants.histogramFileName)
            

main()