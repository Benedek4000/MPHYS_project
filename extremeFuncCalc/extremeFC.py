from spacepy import pycdf
from tqdm import tqdm
from tqdm import trange
import matplotlib.pyplot as plt
import numpy as np
import os.path as path
import os
import math
import extreme_constants as constants

def importFile(combinedFileName, labels):
    with pycdf.CDF(combinedFileName) as fileData:
        bin_structure = fileData[labels[0]][:]
        no_of_entries = fileData[labels[1]][:]
        bin_contents = []
        for i in range(9):
            bin_contents.append(fileData[labels[i+2]][:])
        plotLabels = fileData[labels[11]][:]
        mean = fileData[labels[12]][:]
        std_dev = fileData[labels[13]][:]
    return bin_structure, no_of_entries, bin_contents, mean, std_dev, plotLabels
def main(lPath, combinedFileName, labels, sigmaCutoff, save, plotFileName):
    bin_structure, no_of_entries, bin_contents, mean, std_dev, plotLabels = importFile(combinedFileName, labels)

main(constants.lPath, constants.combinedFileName, constants.labels, constants.sigmaCutoff, constants.save, constants.plotFileName)