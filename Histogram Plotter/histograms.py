from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import os.path as path
import os
import math
import histogram_constants as constants

"""
combined CDF structure:

BGSM_structure: [bin1 lower limit, bin width, number of bins]
BGSM_no_of_entries: [x_entries, y_entries, z_entries]
BGSM_X: [number of entries in each bin in order in the X histogram]
BGSM_Y: [number of entries in each bin in order in the Y histogram]
BGSM_Z: [number of entries in each bin in order in the Z histogram]
labels: [labelX, labelY, labelZ]
mean: [meanX, meanY, meanZ]
std_dev: [standard deviation X, standard deviation Y, standard deviation Z]
"""

"""
contents of constants.py:

lPath = '/home/MPHYS/Data/'
fileListName = path.join(lPath,'fileNames.txt')
fileLengthName = path.join(lPath+'fileLength.txt')
combinedFileName = path.join(lPath+'combined.cdf')
memmapFileName = path.join(lPath, 'data.dat')
labels = ['BGSM_structure', 'BGSM_no_of_entries', 'BGSM_X', 'BGSM_Y', 'BGSM_Z', 'labels', 'mean', 'std_dev']
original_labels = ['BGSM', 'label_bgsm']
bin_structure = [-50, 0.2, 500] #[bin1 lower limit, bin width, number of bins]

save = False #True to save the plot, False to show the plot
histogramFileName = path.join(lPath, 'histogramFull.png')
"""

def fixData(data): #replaces too high and too low values with None
    for i in trange(len(data), desc='Invalidating Erroneous Data', miniters=100000):
        for j in range(len(data[i])-1):
            if (data[i][j] < -1e5 or data[i][j] > 1e5) or (data[i][j] == 0):
                data[i][j] = None
    return data

def importFilenames(filePath, fileListName): #importing filenames
    return list((filePath+i[:-1]) for i in open(fileListName, 'r'))[:-1] #[:-1]s remove the \n from the end of each line and remove the txt filename from the list respectively

def setupNumpyArray(fileLengthName, filenames, original_labels, memmapName): #setting up numpy array
    if path.isfile(fileLengthName):
        with open(fileLengthName, 'r') as f:
            dataLength = int(f.read())
        print('Array has been set up.')
    else:
        dataLength = sum(len(pycdf.CDF(i)[original_labels[0]][:]) for i in tqdm(filenames, desc='Setting Up Numpy Array'))
        with open(fileLengthName, 'w') as f:
            f.write(str(dataLength))
    return np.memmap(memmapName, dtype=float, mode='w+', shape=(dataLength,4))

def updateWelford(count, mean, M2, newValue):
    # For a new value newValue, compute the new count, new mean, the new M2.
    # mean accumulates the mean of the entire dataset
    # M2 aggregates the squared distance from the mean
    # count aggregates the number of samples seen so far
    delta = [0,0,0,0,0,0,0,0,0]
    delta2 = [0,0,0,0,0,0,0,0,0]
    for i in range(len(newValue)):
        if math.isnan(newValue[i]) == False:
            count[i] += 1
            delta[i] = newValue[i] - mean[i]
            mean[i] += delta[i] / count[i]
            delta2[i] = newValue[i] - mean[i]
            M2[i] += delta[i] * delta2[i]
    return count, mean, M2

def finalizeWelford(count, mean, M2): # Retrieve the mean, standard deviation, variance and sample variance
    std_dev = [0,0,0,0,0,0,0,0,0]
    variance = [0,0,0,0,0,0,0,0,0]
    sampleVariance = [0,0,0,0,0,0,0,0,0]
    for i in range(len(count)):
        variance[i] = M2[i] / count[i]
        std_dev[i] = math.sqrt(variance[i])
        sampleVariance[i] = M2[i] / (count[i] - 1)
    return (mean, std_dev, variance, sampleVariance)

"""def calculateStats(data):
    count = [0,0,0,0,0,0,0,0,0]
    mean = [0,0,0,0,0,0,0,0,0]
    M2 = [0,0,0,0,0,0,0,0,0]
    for i in trange(len(data), desc='Calculating \u03BC and \u03C3', miniters=10000):
        count, mean, M2 = updateWelford(count, mean, M2, data[i])
    mean, std_dev, variance, sampleVariance = finalizeWelford(count, mean, M2)
    return mean, std_dev"""

def calculateStats(bin_contents, bin_structure, entry_no):
    mean = [0,0,0,0,0,0,0,0,0]
    std_dev = [0,0,0,0,0,0,0,0,0]
    for i in trange(len(bin_contents), desc='Calculating \u03BC and \u03C3', miniters=10000):
        for j in range(len(bin_contents[i])):
            mean[i] += bin_contents[i][j]*(bin_structure[0]+(0.5+j)*bin_structure[1])
        mean[i] = mean[i]/entry_no[i]
        for j in range(len(bin_contents[i])):
            std_dev[i] += bin_contents[i][j]*((bin_structure[0]+(0.5+j)*bin_structure[1]-mean[i]))**2
        std_dev[i] = math.sqrt(std_dev[i]/entry_no[i])
    return mean, std_dev


"""def calculateStats(data, entry_no, fileLengthName): #USES TRADITIONAL METHODS INSTEAD OF WELFORD'S ALGORITHM, BUT SLOWER
    with open(fileLengthName, 'r') as f:
            dataLength = int(f.read())
    #mean = list(sum(data[j][i] for j in trange(entry_no[i], desc='Calculating mean '+str(i+1)+'/3'))/entry_no[i] for i in range(3))
    mean = [0,0,0]
    std_dev = [0,0,0]
    mean_counter = [0,0,0]
    std_dev_counter = [0,0,0]
    print('entry_no:',entry_no)
    for i in range(3):
        for j in trange(dataLength, desc='Calculating mean '+str(i+1)+'/3'):
            if math.isnan(data[j][i]) == False:
                mean[i] += data[j][i]/entry_no[i]
                mean_counter[i] += 1
    print('mean_counter',mean_counter)
    print('mean:',mean)
    #std_dev = list(math.sqrt((sum((data[j][i]-mean[i])**2 for j in trange(entry_no[i], desc='Calculating standard deviation '+str(i+1)+'/3')))/entry_no[i]) for i in range(3))
    for i in range(3):
        for j in trange(dataLength, desc='Calculating standard deviation '+str(i+1)+'/3'):
            if math.isnan(data[j][i]) == False:
                std_dev[i] += (data[j][i]-mean[i])**2
                std_dev_counter[i] += 1
        std_dev[i] = math.sqrt(std_dev[i]/entry_no[i])
    print('std_dev_counter:',std_dev_counter)
    print('std_dev:',std_dev)
    return mean, std_dev"""

def processData(filenames, combinedFileName, solarFileName, labels, original_labels, data, bin_structure): #processing data
    if path.isfile(combinedFileName): #imports data from combined.cdf if it exists
        with pycdf.CDF(combinedFileName) as dataFile:
            print('Importing data from '+combinedFileName)
            bin_structure = dataFile[labels[0]][:]
            entry_no = dataFile[labels[1]][:]
            bin_contents = [dataFile[labels[2]][:], dataFile[labels[3]][:], dataFile[labels[4]][:], dataFile[labels[5]][:], dataFile[labels[6]][:], dataFile[labels[7]][:], dataFile[labels[8]][:], dataFile[labels[9]][:], dataFile[labels[10]][:]]
            axis_labels = dataFile[labels[11]][:]
            mean = dataFile[labels[12]][:]
            std_dev = dataFile[labels[13]][:]
    else: #imports data from the original files if combined.cdf does not exist, 
            #then filters erroneous data, distributes data into bins and calculates statistics for the data. then, data is saved along with statistics into combined.cdf
        orig_axis_labels = pycdf.CDF(filenames[0])[original_labels[2]][:]
        axis_labels = []
        for i in ['Minimum ', 'Intermediate ', 'Maximum ']:
            for j in orig_axis_labels:
                axis_labels.append(i+j)
        counter = 0
        for currentFileName in tqdm(filenames, desc='Importing Data'):
            with pycdf.CDF(currentFileName) as currentFile:
                counter_saved = counter
                for currentLine in currentFile[original_labels[0]][:]:
                    data[counter] = np.append(currentLine, 0)
                    counter += 1
                for currentDate in currentFile[original_labels[1]][:]:
                    data[counter_saved][3] = currentDate.year*12+currentDate.month
                    counter_saved += 1
        data = fixData(data)
        #import solar periods
        with pycdf.CDF(solarFileName) as solarFile:
            solarPeriods = []
            for i in range(len(solarFile['start'][:])):
                solarPeriods.append([solarFile['start'][i], solarFile['end'][i], solarFile['type'][i]])
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
        entry_no = [0,0,0,0,0,0,0,0,0] #min(x,y,z), int(x,y,z), max(x,y,z)
        bin_contents = np.zeros((9, bin_structure[2]), dtype=float)
        for currentLine in tqdm(data, desc='Distributing Data Into Bins', miniters=100000):
            offset = 0
            if currentLine[3] in minList:
                offset = 0
            if currentLine[3] in intList:
                offset = 3
            if currentLine[3] in maxList:
                offset = 6
            for i in range(3):
                if currentLine[i] >= bin_structure[0] and currentLine[i] < (bin_structure[0]+bin_structure[1]*bin_structure[2]):    
                    bin_contents[i+offset][math.floor((currentLine[i]-bin_structure[0])/bin_structure[1])] += 1
                    entry_no[i+offset] += 1
        mean, std_dev = calculateStats(bin_contents, bin_structure, entry_no)#does not use welford anymore
        #mean, std_dev = calculateStats(data, entry_no, constants.fileLengthName) #USES TRADITIONAL METHODS INSTEAD OF WELFORD'S ALGORITHM, BUT SLOWER
        print('Exporting data into '+combinedFileName)
        pycdf.lib.set_backward(False)
        saveFile = pycdf.CDF(combinedFileName, '')
        saveFile[labels[0]] = bin_structure
        saveFile[labels[1]] = entry_no
        for i in range(9):
            saveFile[labels[i+2]] = bin_contents[i]
        saveFile[labels[11]] = axis_labels
        saveFile[labels[12]] = mean
        saveFile[labels[13]] = std_dev
        saveFile.close()
        os.remove(constants.MFImemmapFileName)
    return bin_contents, entry_no, axis_labels, mean, std_dev

def plotData(processedData, entryNo, bin_structure, axisLabels, save, histogramFileName, mean, std_dev):
    fig, axs = plt.subplots(nrows=3, ncols=3)
    for i, ax in tqdm(enumerate(axs.flat), desc='Plotting Data'):
        x_axis = np.linspace(bin_structure[0]+0.5*bin_structure[1], bin_structure[0]+bin_structure[1]*bin_structure[2]+0.5*bin_structure[1], num = bin_structure[2])
        #x_axis: start = bin1_lower_limit+0.5*bin_width, stop = bin1_lower_limit+bin_width*no_of_bins+0.5*bin_width, num = no_of_bins
        ax.plot(x_axis, processedData[i]/entryNo[i])
        ax.set(xlabel=axisLabels[i], ylabel='log % Occurence')
        ax.set_yscale('log')    
        ax.axvline(mean[i], color='red', linewidth=1.5, label='\u03BC = '+'{0:.3f}'.format(mean[i]))
        ax.axvline(mean[i]+std_dev[i], color='green', linewidth=0.5, label='\u03C3 = '+'{0:.3f}'.format(std_dev[i]))
        ax.axvline(mean[i]-std_dev[i], color='green', linewidth=0.5)
        ax.axvline(mean[i]+3*std_dev[i], color='red', linewidth=1.0, label='3\u03C3 = '+'{0:.3f}'.format(3*std_dev[i]))
        ax.axvline(mean[i]-3*std_dev[i], color='red', linewidth=1.0)
        ax.axvline(mean[i]+4*std_dev[i], color='black', linewidth=1.0, label='4\u03C3 = '+'{0:.3f}'.format(4*std_dev[i]))
        ax.axvline(mean[i]-4*std_dev[i], color='black', linewidth=1.0)
        ax.axvline(mean[i]+5*std_dev[i], color='purple', linewidth=1.0, label='5\u03C3 = '+'{0:.3f}'.format(5*std_dev[i]))
        ax.axvline(mean[i]-5*std_dev[i], color='purple', linewidth=1.0)
        ax.legend(loc='upper right')
    if save:
        plt.savefig(histogramFileName, dpi=100)
    else:
        plt.show()
    return None

def main():
    MFIfilenames = importFilenames(constants.MFIPath, constants.MFIfileListName)
    data = setupNumpyArray(constants.MFIfileLengthName, MFIfilenames, constants.MFI_labels, constants.MFImemmapFileName)
    processedData, entryNo, axisLabels, mean, std_dev = processData(MFIfilenames, constants.MFIcombinedFileName, constants.solarActivityFileName, constants.labels, constants.MFI_labels, data, constants.bin_structure)
    plotData(processedData, entryNo, constants.bin_structure, axisLabels, constants.save, constants.histogramFileName, mean, std_dev)
    
main()