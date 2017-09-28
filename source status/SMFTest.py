import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

T = np.loadtxt('Trasmissione.CSV')
R = np.loadtxt('Riflessione.CSV')

lenT = len(T[:,1])
lenR = len(R[:,1])

length = min(lenR,lenT) - 1500
shift = 0

mstomin = 1e-4/6.
Ttime = T[:length,1]*mstomin
Rtime = R[:length,1]*mstomin
Tint = T[:length,0]
Rint = R[shift:length+shift,0]

#plt.plot(Ttime, Tint)
#plt.plot(Rtime, Rint*96)
#plt.plot(Rtime, Rint+Tint)
#plt.show()

plt.plot(Rtime, Rint/Tint*96.)
plt.xlabel('Time [min]')
plt.ylabel('Reflected/Transmitted * 96')
#plt.show()
plt.savefig('Reflected over Transmitted')