from tqdm import tqdm
from tqdm import trange
import numpy as np
from spacepy import pycdf
import matplotlib.pyplot as plt
import datetime
import solar_constants as constants

Rfilenames = list((constants.RPath+i[:-1]) for i in open(constants.RfileListName, 'r'))[:-1]
"""times = list(pycdf.CDF(i)['Epoch'][len(pycdf.CDF(i)['Epoch'][:])] for i in tqdm(Rfilenames))
#data = list(sum(pycdf.CDF(i)['R'][j] for j in range(len(pycdf.CDF(i)['R'][:]))) for i in tqdm(Rfilenames))
for i in times:
    print(i)"""

times = []
for j in tqdm(Rfilenames):
    with pycdf.CDF(j) as currentFile:
        for i in currentFile['Epoch'][:]:
            if len(times) == 0:
                times.append(i.year*12+i.month)
            elif times[-1] != (i.year*12+i.month):
                times.append(i.year*12+i.month)

shift = times[0]
values = []
for i in range(len(times)):
    values.append(0)
for j in tqdm(Rfilenames):
    with pycdf.CDF(j) as currentFile:
        epochData = currentFile['Epoch'][:]
        rData = currentFile['R'][:]
        for i in range(len(epochData)):
            date = epochData[i]
            values[date.year*12+date.month-shift] += rData[i]

data = []
for i in range(len(times)):
    data.append([times[i], values[i]])
    print(data[i])

plt.xticks(np.arange(1960, 2030, 5))
plt.plot([x/12 for x in times], values)
plt.show()