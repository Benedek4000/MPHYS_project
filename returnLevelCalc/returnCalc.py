from spacepy import pycdf
import os.path as path
import sys
import math

lPath = '/home/MPHYS/Data/'
MFI_parameter_file=path.join(lPath, 'MFIparameters.cdf')
SWE_parameter_file=path.join(lPath, 'SWEparameters.cdf')
P_parameter_file=path.join(lPath, 'Pparameters.cdf')

dataset=sys.argv[1]
activity=sys.argv[2]
coordinate=sys.argv[3]
minmax=sys.argv[4]
levper=sys.argv[5]
value=float(sys.argv[6])

if dataset=='MFI':
    p_file=MFI_parameter_file
elif dataset=='SWE':
    p_file=SWE_parameter_file
elif dataset=='P':
    p_file=P_parameter_file

if activity=='min':
    activity=0
elif activity=='int':
    activity=1
elif activity=='max':
    activity=2

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
    
    if dataset=='P':
        [xi, mu, sigma] = parameters[activity][minmax]
    else:
        [xi, mu, sigma] = parameters[activity][coordinate][minmax]
    
    if levper=='period':
        if minmax==0: #minima
            result=-mu+sigma/xi*(1-(-math.log(1-1/(365*value)))**(-xi))
        elif minmax==0: #maxima
            result=mu-sigma/xi*(1-(-math.log(1-1/(365*value)))**(-xi))
        print('Return Level = '+str(result)+" nT or km/s or nPa")
    elif levper=='level':
        if minmax==0: #minima
            result=(1/365)/(1-math.e**(-(1+xi/sigma*(-value-mu))**(-1/xi)))
        elif minmax==1: #maxima
            result=(1/365)/(1-math.e**(-(1+xi/sigma*(value-mu))**(-1/xi)))
        print('Return Period = '+str(result)+" years")