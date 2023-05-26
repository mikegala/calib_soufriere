# -*- coding: utf-8 -*-
from pylab import *

### processing function
def store(var,textFile):
    data=loadtxt(textFile,skiprows=1)
    it=[]
    t=[]
    e1=[]
    e2=[]
    e3=[]
    s1=[]
    s2=[]
    s3=[]
    tc=[]
    sc=[]
    unbF=[]
    for i in range(0,len(data)):
      it.append(float(data[i,3]))
      t.append(float(data[i,10]))
      e1.append(-float(data[i,0]))
      e2.append(-float(data[i,1]))
      e3.append(-float(data[i,2]))
      s1.append(-float(data[i,4]))
      s2.append(-float(data[i,5]))
      s3.append(-float(data[i,6]))
      sc.append(float(data[i,7]))
      tc.append(float(data[i,9]))
      unbF.append(float(data[i,10]))
    var.append(it)
    var.append(t)
    var.append(e1)
    var.append(e2)
    var.append(e3)
    var.append(s1)
    var.append(s2)
    var.append(s3)
    var.append(tc)
    var.append(sc)
    var.append(unbF)

### data input
dataFile1='Triax_calib_A0.25_Y40_C100_T5_250kPa'
a1=[]
store(a1,dataFile1)

dataFile2='Triax_calib_A0.25_Y40_C100_T5_50kPa'
a2=[]
store(a2,dataFile2)

dataFile3='Triax_calib_A0.25_Y40_C100_T5_2.5kPa'
a3=[]
store(a3,dataFile3)

dataFile4='Triax_calib_A0.25_Y40_C100_T5_0.5kPa'
a4=[]
store(a4,dataFile4)

dataFile5='Triax_calib_A0.25_Y40_C100_T5_10Pa'
a5=[]
store(a5,dataFile5)

# s1max=[]
# s3max=[]
# fail=[]
# for i in range(1,6):
#   s1max.append(max((globals()["a%i" % i][5])))
#   s3max.append(max((globals()["a%i" % i][7])))
# fail.append(s1max)
# fail.append(s3max)


### data plot
rcParams.update({'legend.numpoints':1,'font.size': 20,'axes.labelsize':25,'xtick.major.pad':10,'ytick.major.pad':10,'legend.fontsize':20})
lw=2
ms=5

## no es sigma1 

#figure(1,figsize=(14,10))
#ax1=subplot(1,1,1)
#xlabel(r'$\varepsilon_1$ [$10^{-3}$]')
#xlabel(r'$\sigma_3$ [MPa]')
#plot([x/1e6 for x in fail[0]],[x/1e6 for x in fail[1]],'-ok',linewidth=lw,)
#plot([x*1000 for x in a1[4]],[x*1000 for x in a1[2]],'-b',linewidth=lw,label='A0.2')
#plot([x*1000 for x in a2[4]],[x*1000 for x in a2[2]],'-r',linewidth=lw,label='A0.25')
#plot([x*1000 for x in a3[4]],[x*1000 for x in a3[2]],'-k',linewidth=lw,label='A0.050')
#plot([x*1000 for x in a4[4]],[x*1000 for x in a4[2]],'-g',linewidth=lw,label='A0.100')
#ylabel(r'$\varepsilon_3$ [$10^{-3}$]')
# ylabel(r'$\sigma_1$ [MPa]')
#axis(xmax=2.5,ymin=-1)
#ticklabel_format(axis='both', style='sci', scilimits=(0,0))
#legend(loc="best")
#ticklabel_format(axis='both', style='sci', scilimits=(0,0))
#savefig(dataFile1+'_Acalibration_threshold.tiff',dpi=200,format='tiff',transparent=False)

# # ### show or save
#show()

figure(1,figsize=(14,10))
ax1=subplot(1,1,1)
xlabel(r'$\varepsilon_1$ [$10^{-3}$]')
## xlabel(r'$\sigma_3$ [MPa]')
plot([x*1000 for x in a1[4]],[(i-j)/1e6 for i, j in zip(a1[7],a1[5])],'-k',linewidth=lw,label='conf250kPa')
plot([x*1000 for x in a2[4]],[(i-j)/1e6 for i, j in zip(a2[7],a2[5])],'-r',linewidth=lw,label='conf50kPa')
plot([x*1000 for x in a3[4]],[(i-j)/1e6 for i, j in zip(a3[7],a3[5])],'-b',linewidth=lw,label='conf2.5kPa')
plot([x*1000 for x in a4[4]],[(i-j)/1e6 for i, j in zip(a4[7],a4[5])],'-g',linewidth=lw,label='conf0.5kPa')
plot([x*1000 for x in a5[4]],[(i-j)/1e6 for i, j in zip(a5[7],a5[5])],'-y',linewidth=lw,label='conf10Pa')
## plot([x*1000 for x in a1[4]],[i/1e6 for i, j in zip(a1[7],a1[5])],'-k',linewidth=lw)
##plot([x*1000 for x in a1[7]],[x*1000 for x in a1[5]],'-k',linewidth=lw)
#ylabel(r'$\sigma_1$ [MPa]')
ylabel(r'$\sigma_1$ - $\sigma_3$  [MPa]')
#axis(ymin=0)
ticklabel_format(axis='both', style='sci', scilimits=(0,0))
legend(loc="best")
# ax2=ax1.twinx()
# ax2.plot([x*1000 for x in a1[4]],a1[8],'-b',linewidth=lw)
# ax2.plot([x*1000 for x in a1[4]],a1[9],'-r',linewidth=lw)
# ax2.plot([x*1000 for x in a1[4]],[(i+j) for i, j in zip(a1[8],a1[9])],'--k',linewidth=lw)
# ylabel('number of cracks [-]')
# legend(('tensile','shear','total'),loc=2)
# ticklabel_format(axis='both', style='sci', scilimits=(0,0))
#savefig(dataFile1+'_SIG1vsEPS.tiff',dpi=200,format='tiff',transparent=False)
show()
