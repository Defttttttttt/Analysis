import time
import datetime
import pymysql
import numpy as np
import thinkdsp
import thinkplot
import GenCalcParaFromCSV
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import redis
cos_sig=thinkdsp.CosSignal(freq=440,amp=1.0,offset=0)
sin_sig=thinkdsp.SinSignal(freq=880,amp=0.5,offset=0)
mix=cos_sig+sin_sig
wave=mix.make_wave(duration=0.5,start=0,framerate=11025)
# print(wave)
# period=mix.period
# segment=wave.segment(start=0,duration=period*3)
wave.plot()
thinkplot.show()
a={'1':1,'2':2}
for i in a:
    print(i)