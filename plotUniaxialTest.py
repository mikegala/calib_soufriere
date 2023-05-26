# -*- coding: utf-8 -*-
from pylab import *

### processing function
def store(var,textFile):
    data=loadtxt(textFile,skiprows=1)
    it=[]
    eps=[]
    sig=[]
    tc=[]
    sc=[]
    te=[]
    se=[]
    ubf=[]
    for i in range(0,len(data)):
      it.append(float(data[i,1]))
      eps.append(abs(float(data[i,0])))
      sig.append(abs(float(data[i,3])))
      tc.append(float(data[i,4]))
      sc.append(float(data[i,2]))
      ubf.append(float(data[i,5]))
    var.append(it)
    var.append(eps)
    var.append(sig)
    var.append(tc)
    var.append(sc)
    var.append(ubf)
   
### data input
dataFile1='Comp_C100_Y40_A0.25_T5.0_por0.3'
dataFile2='Comp_C280_Y40_A0.25_T5.0_por0.3'
#dataFile3='Comp_cal__0.1_A5'

a1=[]
store(a1,dataFile1)

a2=[]
store(a2,dataFile2)

#a3=[]
#store(a3,dataFile3)

rcParams.update({'legend.numpoints':1,'font.size': 20,'axes.labelsize':25,'xtick.major.pad':10,'ytick.major.pad':10,'legend.fontsize':20})
lw=2
ms=10

### plots

#figure(0,figsize=(12,10))
#ax1=subplot(1,1,1)
#xlabel('iteration [-]')
#ax1.plot(a1[0],[x/1e6 for x in a1[2]],'-k',linewidth=lw)
#ylabel(r'$\sigma_1$ [MPa]')
#ax2 = ax1.twinx()
#ax2.plot(a1[0],a1[5],'-r',linewidth=lw)
#ylabel('unbForce [-]')

figure(1,figsize=(10,10))
ax1=subplot(1,1,1)
xlabel(r'$\varepsilon_1$ $10^{-3}$]')
plot([x*1e3 for x in a1[1]],[x/1e6 for x in a1[2]],'-k',linewidth=lw,label='C100')
plot([x*1e3 for x in a2[1]],[x/1e6 for x in a2[2]],'-r',linewidth=lw,label='C280')
ylabel(r'$\sigma_1$ [MPa]')
legend(loc="best")

#figure(2,figsize=(12,10))
#ax1=subplot(1,1,1)
#xlabel(r'$\varepsilon_1$ [$10^{-3}$]')
##axis(xmin=0,xmax=0.12)
## ax1.plot([x*1e3 for x in a1[1]],[x/1e6 for x in a1[2]],'-k',linewidth=lw, label= 'A0.15')
#ax1.plot([x*1e3 for x in a2[1]],[x/1e6 for x in a2[2]],'-b',linewidth=lw, label= 'A0.20')
#ax1.plot([x*1e3 for x in a3[1]],[x/1e6 for x in a3[2]],'-r',linewidth=lw, label= 'A0.30')
#ylabel(r'$\sigma_1$ [MPa]')
#ticklabel_format(axis='both', style='sci', scilimits=(0,0))
## ax2 = ax1.twinx()
## ax2.plot([x*1e3 for x in a1[1]],a1[3],'-b',linewidth=lw)
## ax2.plot([x*1e3 for x in a1[1]],a1[4],'-r',linewidth=lw)
## ylabel('number of cracks [-]')
#legend(loc="best")
#ticklabel_format(axis='both', style='sci', scilimits=(0,0))

### show or save
show()
