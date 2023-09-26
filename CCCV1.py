# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 17:20:52 2023

@author: cebal
"""

#Opción 2 de CCCV

import numpy as np
import matplotlib.pyplot as plt


#Datos dados
Cmax = 72000 #Wh (ioniq5) https://www.hyundai.cl/content/uploads/ficha-tecnica-ioniq-5-21.5x28-cm-web-1.pdf
Vmax = 650 #V (ioniq5)
P_cargador = 30000 #W
soci=0.2
socf=0.9
dt=0.001 #h
dt2=dt
tlineal=(Cmax*socf-Cmax*soci)/P_cargador
taprox=1.61*tlineal

Iin=P_cargador/Vmax #Corriente que se usará para corriente constante, se encuentra el punto de
#máxima potencia y se considera que ahí es la potencia del cargador.

#condiciones de borde
#I[n]=0
#V[n]=Vmax
Vin=Cmax*soci/Iin #supuesto fuerte
Pin=Vin*Iin
Cin=Cmax*soci
#C[n]=Cmax*socf

#linealidad voltaje en CC
dV=((Vmax-Vin)/(taprox/2))*dt
dV2=dV

#linealidad corriente en CV
dI=(-Iin/(taprox/2))*dt
dI2=dI

tiempo=[0]
I=[Iin]
V=[Vin]


while V[-1]<Vmax:
    I.append(Iin)
    tiempo.append(dt)
    dt=dt+dt2
    V.append(Vin + dV)
    dV=dV+dV2
    
while I[-1]>0:
    V.append(Vmax)
    tiempo.append(dt)
    dt=dt+dt2
    I.append(Iin+dI)
    dI=dI+dI2
    
P=np.zeros(len(I))
C=[Cin]


for i in range(len(I)):
    P[i]=V[i]*I[i]

i=1
while i<len(P):
    C.append(C[i-1] + P[i]*dt2)
    i=i+1
    


fig,ax=plt.subplots(2,2)
ax[0,0].plot(tiempo, V)
ax[0,1].plot(tiempo, I)
ax[1,0].plot(tiempo, C)
ax[1,1].plot(tiempo, P)
ax[0,0].set_xlabel('Time (h)'); ax[0,0].set_ylabel('Voltaje (V)')
ax[0,1].set_xlabel('Time (h)'); ax[0,1].set_ylabel('Corriente (I)')
ax[1,0].set_xlabel('Time (h)'); ax[1,0].set_ylabel('Carga (Wh)')
ax[1,1].set_xlabel('Time (h)'); ax[1,1].set_ylabel('potencia (W)')


SOC=np.zeros(len(C))
for i in range(len(C)):
    SOC[i]=C[i]/Cmax

#plt.plot(tiempo,SOC)

print(SOC[-1])