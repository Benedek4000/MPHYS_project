from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import os.path as path
import os
import math
import datetime as dt
import vb_constants as constants
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
                nextday = currentSWEEpoch+dt.timedelta(days=1)
                swedata[str(1000000*nextday.year+10000*nextday.month+100*nextday.day+nextday.hour)[:10]] = [None, None, None]
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

def distributeBins(data, Vbins, Bbins):
    #data: lots of records, each line: data[0]=V, data[1]=B
    #bin structure: [bin1 lower limit, bin width, number of bins]
    bin_contents = np.zeros((Vbins[2], Bbins[2]), dtype=float)
    entry_no = 0
    for currentLine in tqdm(data, desc='Distributing Data Into Bins', miniters=100000):
        if (currentLine[0] >= Vbins[0] and currentLine[0] < (Vbins[0]+Vbins[1]*Vbins[2])) and (currentLine[1] >= Bbins[0] and currentLine[1] < (Bbins[0]+Bbins[1]*Bbins[2])):    
            bin_contents[math.floor((currentLine[0]-Vbins[0])/Vbins[1])][math.floor((currentLine[1]-Bbins[0])/Bbins[1])] += 1
            entry_no += 1
    return bin_contents, entry_no

def saveData(fileName, data, Vbins, Bbins, labels):
    print('Exporting data into '+fileName)
    pycdf.lib.set_backward(False)
    saveFile = pycdf.CDF(fileName, '')
    saveFile[labels[0]] = Vbins
    saveFile[labels[1]] = Bbins
    for i in range(4):
        saveFile[labels[i+2]] = data[i]
    saveFile.close()

def processData(data):
    arraysize=len(data)
    heatmap = []
    for i in trange(4, desc='Preparing Data for Distribution'):
        arrayToPlot = np.memmap(constants.lPath+'dataToPlot'+'.dat', dtype=float, mode='w+', shape=(arraysize,2))
        if i != 3:
            for index, j in enumerate(data):
                arrayToPlot[index][0] = j[i+4]
                arrayToPlot[index][1] = j[i+1]
        else:
            for index, j in enumerate(data):
                arrayToPlot[index][0] = math.sqrt(j[4]**2+j[5]**2+j[6]**2)
                arrayToPlot[index][1] = math.sqrt(j[1]**2+j[2]**2+j[3]**2)
        h,e = distributeBins(arrayToPlot, constants.Vbin_structure, constants.Bbin_structure)#, range=[[-40,40],[-900,-200]])
        entry_no = [0,0,0,0]
        heatmap.append(h/e)
        entry_no[i] = e
    return heatmap

def plotData(heatmap, Vbins, Bbins, save, histogramFileName):

    fig = plt.figure()

    xedges=[Bbins[0], Bbins[0]+Bbins[1]*Bbins[2]]
    yedges=[Vbins[0]+Vbins[1]*Vbins[2], Vbins[0]]

    fig.suptitle('Solar Wind Velocity against Magnetic Field Strength heatmap', fontsize=16)

    ax1=fig.add_subplot(221)
    ax1.set(xlabel='B (nT) in XGSM', ylabel='V (km/s) in XGSM')
    im1 = ax1.imshow(heatmap[0][:35,:], cmap='hot_r', interpolation='nearest', aspect='auto', norm=LogNorm(vmin=10**-8, vmax=0.01), extent=[xedges[0], xedges[-1], yedges[0]-(yedges[0]-yedges[1])*65/100, yedges[-1]])
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im1, cax=cax, orientation='vertical')
    
    ax2=fig.add_subplot(222)
    ax2.set(xlabel='B (nT) in YGSM', ylabel='V (km/s) in YGSM')
    im2 = ax2.imshow(heatmap[1][25:75,:], cmap='hot_r', interpolation='nearest', aspect='auto', norm=LogNorm(vmin=10**-8, vmax=0.01), extent=[xedges[0], xedges[-1], yedges[0]-(yedges[0]-yedges[1])/4, yedges[-1]+(yedges[0]-yedges[1])/4])
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im2, cax=cax, orientation='vertical')

    ax3=fig.add_subplot(223)
    ax3.set(xlabel='B (nT) in ZGSM', ylabel='V (km/s) in ZGSM')
    im3 = ax3.imshow(heatmap[2][25:75,:], cmap='hot_r', interpolation='nearest', aspect='auto', norm=LogNorm(vmin=10**-8, vmax=0.01), extent=[xedges[0], xedges[-1], yedges[0]-(yedges[0]-yedges[1])/4, yedges[-1]+(yedges[0]-yedges[1])/4])
    divider = make_axes_locatable(ax3)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im3, cax=cax, orientation='vertical')

    ax4=fig.add_subplot(224)
    ax4.set(xlabel='|B| (nT)', ylabel='|V| (km/s)')
    im4 = ax4.imshow(heatmap[3][55:,50:], cmap='hot_r', interpolation='nearest', aspect='auto', norm=LogNorm(vmin=10**-8, vmax=0.01), extent=[0, xedges[-1], -yedges[-1], 1800*0.55-1000])
    divider = make_axes_locatable(ax4)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im4, cax=cax, orientation='vertical')

    fig.subplots_adjust(wspace=0.25)
    if save:
        fig.set_size_inches(17, 10)
        plt.savefig(histogramFileName, dpi=100, bbox_inches='tight')
    else:
        plt.show()
    return None

def main():
    combinedFileName = constants.VBcombinedFileName
    labels = constants.labels
    if path.isfile(combinedFileName):
        with pycdf.CDF(combinedFileName) as dataFile:
            print('Importing data from '+combinedFileName)
            Vstructure = dataFile[labels[0]][:]
            Bstructure = dataFile[labels[1]][:]
            heatmap = [dataFile[labels[2]][:], dataFile[labels[3]][:], dataFile[labels[4]][:], dataFile[labels[5]][:]]
    else:
        MFIfilenames = importFilenames(MFIPath, MFIfileListName)
        SWEfilenames = importFilenames(SWEPath, SWEfileListName)
        data = setupNumpyArray(MFIfileLengthName, MFIfilenames, original_MFI_labels, VBmemmapFileName)
        data = importData(data, MFIfilenames, SWEfilenames, original_MFI_labels, original_SWE_labels)
        data = fixData(data)
        heatmap = processData(data)
        Vstructure = constants.Vbin_structure
        Bstructure = constants.Bbin_structure
        #saveData
        saveData(constants.VBcombinedFileName, heatmap, constants.Vbin_structure, constants.Bbin_structure, constants.labels)
    plotData(heatmap, Vstructure, Bstructure, constants.save, constants.histogramFileName)

main()