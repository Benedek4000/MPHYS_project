import constants
from tqdm import tqdm
from tqdm import trange
from spacepy import pycdf
import matplotlib.pyplot as plt


Rfilenames = list((constants.RPath+i[:-1]) for i in open(constants.RfileListName, 'r'))[:-1]
times = list(pycdf.CDF(i)['Epoch'][0] for i in tqdm(Rfilenames))
data = list(sum(pycdf.CDF(i)['R'][j] for j in range(len(pycdf.CDF(i)['R'][:]))) for i in tqdm(Rfilenames))

plt.plot(times, data)
plt.show()