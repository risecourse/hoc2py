from neuron import h
h.load_file("stdrun.hoc")
h.load_file("nrngui.hoc") # load_file

import numpy as np
from cable import Cable

import matplotlib.pyplot as plt

h.secondorder = 2

varlen = 0

v1 = h.Vector()
v2 = h.Vector()

tvec = []


#%%
# iterpolated time at which voltage = threshold
def where(vec,thresh):# {local i, v1, v2, t1, t2, x
    i = np.argmax(np.array(vec.to_python())>=thresh)
    av1 = vec.x[i-1]
    av2 = vec.x[i]
    at1 = tvec[i-1]
    at2 = tvec[i]
    x = (thresh - av1)/(av2 - av1)
    return at1 + x*(at2 - at1)



# these were not in this code but may be good to add:
# h.finitialize(-65) # * mV)
# h.continuerun(25) # * ms)

#%%
def ict(dist, cbl): # {local i, thresh
    global tvec,  v1, v2
    if (dist > 1000):
        v1 = h.Vector().record(cbl.node[4](1)._ref_v)
        v2 = h.Vector().record(cbl.node[5](0)._ref_v)
        h.dt = .005
        h.tstop = 8
        
    else:
        v1 = h.Vector().record(cbl.node[30](1)._ref_v)
        v2 = h.Vector().record(cbl.node[31](0)._ref_v)
        h.dt = .005
        h.tstop = 3
        
    tvec = np.arange(0,h.tstop + h.dt*.5,h.dt)

    thresh = 50 - 65
    cbl.myL = dist
    cbl.geom()
    h.stdinit()
    h.run()
    #TODO
    t1 = where(v1,thresh) #where(v1, thresh)
    t2 = where(v2,thresh) #where(v2, thresh)
    return Trial(dist, tvec, v1.to_python(), v2.to_python(), t2 - t1)
#%%
class Trial:
    def __init__(self, dist = 0, tvec = [], v1=[], v2=[], isi = -1):
        self.distance = dist
        self.tvec = tvec
        self.v1 = v1
        self.v2 = v2
        self.isi = isi
    
    def __str__(self):
        return f"Trial with internode distance = {self.dist}, isi = {self.isi}"

def main():
    
    mycable = Cable()

    
    stimobj = h.IClamp(mycable.node[0](0.5))
    stimobj.delay = 0 # ms, time after start of sim when you want the current injection to begin
    stimobj.dur = 0.1 # ms, duration of current pulse
    stimobj.amp = 10 # nA, contains the level of current being injected at any given time during simulation   
    #%%
    
    trials = []
    fig1 = len(plt.get_fignums()) + 1
    fig2 = fig1 + 1
    fig3 = fig2 + 1
    for varlen in [25, 50, 100, 200, 1000, 2000, 4000, 6000, 8000, 9000, 9500]:
        newtrial = ict(varlen, mycable)
        trials.append(newtrial)
        plt.figure(fig1)
        plt.plot(newtrial.tvec, newtrial.v1, linewidth=2, label=str(varlen))
        
        plt.figure(fig2)
        plt.plot(newtrial.tvec, newtrial.v2, linewidth=2, label=str(varlen))
            
    plt.figure(fig1)
    plt.title("V1 recorded at end of a node")
    plt.xlabel('t (ms)')
    plt.ylabel('v (mV)')
    plt.legend()
    
    plt.figure(fig2)
    plt.title("V2 recorded at start of next node")
    plt.xlabel('t (ms)')
    plt.ylabel('v (mV)')
    plt.legend()
    
    distances = [x.distance for x in trials]
    isis = [x.isi for x in trials]
    plt.figure(fig3)
    plt.plot(distances, isis)
    plt.title("Internode Spike Interval")
    plt.ylabel('InSI (ms)')
    plt.xlabel('Internodal Length (micron)')
    
    plt.show()
    
    # TODO - plots for the following:
    # g[0].getline(-1, v1, v2)
    # v2 = v1.c.div(v2).mul(1e-3) // factor converts micron/ms to m/s  v2 is velocity
    # v2.line(g[1], v1)
    # v2.c.pow(-1).line(g[2], v1.log10)
    
if __name__=="__main__":
    main()
