from spacepy import pycdf
import os.path as path
import sys
import math

lPath = '/home/MPHYS/Data/'
MFI_parameter_file=path.join(lPath, 'MFIparameters.cdf')
SWE_parameter_file=path.join(lPath, 'SWEparameters.cdf')
P_parameter_file=path.join(lPath, 'Pparameters.cdf')

dataset=sys.argv[1]
coordinate=sys.argv[2]
minmax=sys.argv[3]
levper=sys.argv[4]
value=float(sys.argv[5])

if dataset=='MFI':
    p_file=MFI_parameter_file
elif dataset=='SWE':
    p_file=SWE_parameter_file
elif dataset=='P':
    p_file=P_parameter_file

if coordinate=='x':
    coordinate=0
elif coordinate=='y':
    coordinate=1
elif coordinate=='z':
    coordinate=2

if minmax=='min':
    minmax=0
elif minmax=='max':
    minmax=1

with pycdf.CDF(p_file) as parameter_file:
    parameters = parameter_file['parameters'][:]
    
    results=[]

    for activity in [0,1,2]:
        if dataset=='P':
            [xi, mu, sigma] = parameters[activity][minmax]
        else:
            [xi, mu, sigma] = parameters[activity][coordinate][minmax]
    
        if levper=='period':
            if minmax==0: #minima
                results.append(-mu+sigma/xi*(1-(-math.log(1-1/(365*value)))**(-xi)))
            elif minmax==0: #maxima
                results.append(mu-sigma/xi*(1-(-math.log(1-1/(365*value)))**(-xi)))
        elif levper=='level':
            if minmax==0: #minima
                results.append((1/365)/(1-math.e**(-(1+xi/sigma*(-value-mu))**(-1/xi))))
            elif minmax==1: #maxima
                results.append((1/365)/(1-math.e**(-(1+xi/sigma*(value-mu))**(-1/xi))))

    if levper=='period': #calculate return level
        result=(results[0]+results[1]+results[2])/3
        print('Return Level = '+str(result)+" nT or km/s or nPa")
    elif levper=='level': #calculate return period
        result=3/(1/results[0]+1/results[1]+1/results[2])
        print('Return Period = '+str(result)+" years")
