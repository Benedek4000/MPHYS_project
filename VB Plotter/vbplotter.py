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
    return np.memmap(memmapName, dtype=float, mode='w+', shape=(dataLength,7)) #[bgsm[x,y,z], v_gsm[x,y,z]]

def importFilenames(filePath, fileListName): #importing filenames
    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1] #[:-1]s remove the \n from the end of each line and remove the txt filename from the list respectively

def importData(data, MFIfilenames, SWEfilenames, original_MFI_lables, original_SWE_lables):
    #generate date list
    dates = []
    for i in MFIfilenames: #assuming that for every SWE file, there is an MFI file
        dates.append(i[31:39])
    linkedFiles = {} #a dictionary
    for currentDate in dates:
        MFIname=''
        SWEname=''
        for currentMFI in MFIfilenames:
            if currentDate in currentMFI:
                MFIname = currentMFI
        for currentSWE in SWEfilenames:
            if currentDate in currentSWE:
                SWEname = currentSWE
        if MFIname != '' and SWEname != '':
            linkedFiles[MFIname] = SWEname
    #importing data into data day by day
    counter = 0
    iterator = tqdm(linkedFiles.keys(), desc='Importing Data')
    for currentKey in iterator:
        currentValue = linkedFiles[currentKey]
        with pycdf.CDF(currentKey) as currentMFIfile:
            with pycdf.CDF(currentValue) as currentSWEfile:
                saved_counter = counter
                temp_counter = counter
                for currentMFIEpoch in currentMFIfile[original_MFI_labels[1]][:]:
                    data[counter][0] = 1000000*currentMFIEpoch.year+10000*currentMFIEpoch.month+100*currentMFIEpoch.day+currentMFIEpoch.hour
                    counter += 1
                for currentMFIline in currentMFIfile[original_MFI_labels[0]][:]:
                    for i in range(3):
                        data[temp_counter][i+1] = currentMFIline[i]
                        temp_counter += 1
                swedata = {}
                for index, currentSWEEpoch in enumerate(currentSWEfile[original_SWE_labels[1]][:]):
                    swedata[str(1000000*currentSWEEpoch.year+10000*currentSWEEpoch.month+100*currentSWEEpoch.day+currentSWEEpoch.hour)[:10]] = currentSWEfile[original_SWE_labels[0]][index]
                currentSWEEpoch = currentSWEfile[original_SWE_labels[1]][0]
                swedata[str(1000000*(currentSWEEpoch.year+1)+10000*currentSWEEpoch.month+100*currentSWEEpoch.day+currentSWEEpoch.hour)[:10]] = [None, None, None]
                for i in range(saved_counter, counter, 1):
                    for j in range(3):
                        data[i][j+4] = swedata[str(data[i][0])[:10]][j]
    #OLD VERSION STARTS HERE
    """counter = 0
    for currentFileName in tqdm(MFIfilenames, desc='Importing MFI Data'):
        with pycdf.CDF(currentFileName) as currentFile:
            saved_counter = counter
            for currentEpoch in currentFile[original_MFI_labels[1]][:]:
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
                    data[index][6] = None"""
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
        ax.scatter(xaxis,yaxis, s=2)
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