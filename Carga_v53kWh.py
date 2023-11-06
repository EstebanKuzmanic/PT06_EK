"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import pandas as pd
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from scipy import interpolate



#Datos de la batería y del circuito equivalente
cbat=37 #Ah

ocv=pd.read_csv('ocv.csv') #Sacado del gráfico
RyC=pd.read_csv('RyC.csv') #Sacado de la tesis

i_Ro=interpolate.interp1d(np.array(RyC['SOC']), np.array(RyC['Ro']), kind = 'cubic')
i_R1=interpolate.interp1d(np.array(RyC['SOC']), np.array(RyC['R1']), kind = 'cubic')
i_C1=interpolate.interp1d(np.array(RyC['SOC']), np.array(RyC['C1']), kind = 'cubic')

ocv['Ro']=i_Ro(np.array(ocv['SOC']))
ocv['R1']=i_R1(np.array(ocv['SOC']))
ocv['C1']=i_C1(np.array(ocv['SOC'])) #No sirven realmente

#Modelo de carga

tf=0.9 #ESTO HAY QUE ARREGLARLO O VER OTRA FORMA DE HACERLO
dt=0.0001
t=np.arange(0,tf,dt)
N=5 # número de escalones
te=tf/N

    #Función para el escalón de tiempo
def stepTime(ti,tf,t):
    return np.heaviside(t-ti,1)-np.heaviside(t-tf,1)

    #Función de la corriente MSCC
    #1C - 0.8C - 0.6C - 0.4C - 0.2C
def current(t):
    return stepTime(0,0.4,t)*-1.5*cbat+stepTime(0.4,0.6,t)*-1*cbat+stepTime(0.6,0.7,t)*-0.6*cbat+stepTime(0.7,0.8,t)*-0.3*cbat+stepTime(0.8,0.9,t)*-0.2*cbat

#Resolución del SOC según el tiempo
def batsoc(y, t, i_R1, i_C1, cbat):
    v1, soc = y
    dydt=[-v1/(i_R1(soc)*i_C1(soc))+current(t)/i_C1(soc), -current(t)/cbat]
    return dydt
SOCi=[0,0.05] #condiciones iniciales DADA
solSOC = odeint(batsoc, SOCi, t, args=(i_R1, i_C1, cbat))


i_Voc=interpolate.interp1d(np.array(ocv['SOC']), np.array(ocv['V']), kind = 'cubic')

Voc=i_Voc(np.array(solSOC[:,1]))
r0_t=i_Ro(np.array(solSOC[:,1]))

#Cálculo del voltaje a la salida
V=[]
for i in range(len(t)):
    V_l= Voc[i] - solSOC[:,0][i] - current(t[i])*r0_t[i] #Revisar signos
    V.append(V_l)
    
#Capacidad en cada momento
C=[]
for i in range(len(t)):
    C.append(solSOC[:,1][i]*cbat)

Cvi=[]
for i in range(len(t)):
    Cvi.append(V[i]*-current(t[i])*t[i])

#%%
#Gráficos Estado de la batería

# fig, axes = plt.subplots()
# plt.plot(t, C, color='b')
# plt.plot(t, Cvi, color='r')
# plt.xlabel('tiempo [s]')
# plt.ylabel('carga SOC (azul) carga VI (rojo) [Wh] ')
# plt.title('Comparación de cargas')
# plt.show()

# fig, ax = plt.subplots(3, 1, sharex=True)
# ax[0].plot(t, V, 'y')
# ax[1].plot(t, current(t), 'r')
# ax[2].plot(t, solSOC[:, 1])
# ax[0].set_ylabel('Voltaje (V)')
# ax[1].set_ylabel('Corriente (I)')
# ax[2].set_xlabel('Time (h)')
# ax[2].set_ylabel('Estado de carga')
# fig.suptitle('Estados de una batería')

#%%
#hacemos un banco de baterias
serie=98
paralelo=4
V=np.array(V)
Vt=V*serie
i_t=np.array(current(t)*paralelo)
P=Vt*i_t/1000
V_nominal=3.65 #V
C_nominal= cbat*V_nominal*serie*paralelo/1000 #kWh
C_banco=np.array(C_nominal*solSOC[:,1])



plt.plot(t,P, 'g')
plt.xlabel('tiempo [s]')
plt.ylabel('Potencia [kW]')
plt.title('Potencia demandada')

#%%
plt.plot(t,C_banco)
plt.xlabel('tiempo [s]')
plt.ylabel('Capacidad [kWh]')
plt.title('Capacidad del banco')