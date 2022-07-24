# Brill, Waxman, Moore, and Joyner (1977) Conduction velocity and spike
# configuration in myelinated fibres: Computed dependence on internode distance
# J. Neurology, Neurosurgery, and Psychiatry. 40: 769-774

# Converted from hoc to python by marianne.bezaire@gmail.com
# July 2022

from neuron import h
h.load_file("stdrun.hoc")
h.load_file("nrngui.hoc") # load_file

import math

# converted to a 'Cable' class:
class Cable:
    def __init__(self, nnode=50, myL=1000):
        # replace 
        # create node[1], myelin[1]
        # with:
        self.node = []
        self.myelin = []
        self.nnode = nnode
        self.myL = myL
        self.diam = 10
        self.make()
    
    # topol(nnode) connects an alternating sequence of node/myelin pairs.
    # For internode lengths < 1000 microns more than 12 nodes were used
    # to eliminate end and stimulation effects. Dynamically re-constructing
    # the topology is easy but the stimulator and GUI depend on sections they
    # reference staying in existence. It's especially bad for a PointProcessManager
    # when its entire cell disappears. Therefore, we use 50 nodes
    # throughout which, although overkill for long myelin lengths, is appropriate
    # for the shortest 25 um lengths used in fig 1.
    
    # replace
    # proc topol() {local i ...}
    # with:
    def topol(self):
        # replace
        # create node[nnode], myelin[nnode-1]
        # with:
        for n in range(self.nnode):
            self.node.append(h.Section(name=f"node[{n}]"))
            self.myelin.append(h.Section(name=f"myelin[{n}]"))
        
        # removed:
        # access node[0]
        
        for i in range(self.nnode-1): # 0 thru nnode - 2
            # replace
            # connect myelin[i](0), node[i](1)
            # connect node[i+1](0), myelin[i](1)
            # with:
            self.myelin[i].connect(self.node[i])
            self.node[i+1].connect(self.myelin[i])
        
        # replace
        # forsec "myelin" { nseg = 10 }
        # with:
        for sec in self.myelin:
            sec.nseg = 10
    
    # replace
    # proc geom() {
    #     forsec "node" { # area = 100 um2
    #         L = 3.183
    #         diam = 10
    #     }
    #     forsec "myelin" {
    #         L = $1
    #         diam = 10
    #     }
    # }
    # with:
    def geom(self):
        for sec in self.node:
            sec.L = 3.183
            sec.diam = 10
            
        for sec in self.myelin:
            sec.L = self.myL
            sec.diam = 10
    
    # replace
    # func l2a() { # convert per length (/cm) to per area (/cm2) based on diameter
    #     return 1/(PI*diam) * 1e4
    # }
    # with:
    def l2a(self, diam):
        return 1/(math.pi*diam) * 1e4
    
    # replace
    # proc biophys() {local fac
    # (function body at end of file)
    # with:
    def biophys(self):
        # ohm/cm must be converted to ohm-cm by multiplying by
        # cross sectional area
        
        for sec in self.node + self.myelin:
            fac = math.pi*sec.diam**2/4 * 1e-8
            sec.Ra = 1.26e8 * fac
    
        # paper relative to rest=0 but following values relative to -65
        for sec in self.node:
            sec.insert("hh")
            for seg in sec: 
                seg.hh.gnabar = 1.2
                seg.hh.gkbar = .09
                seg.hh.gl = .02
                seg.na_ion.ena = 115 - 65
                seg.k_ion.ek = -12 - 65
                seg.hh.el = -.05 - 65
                seg.cm = 3.14e-9*self.l2a(sec.diam)*1e6 # end up as uF/cm2
    
        for sec in self.myelin:
            sec.insert("pas")
            for seg in sec: 
                seg.pas.e = -65
                seg.pas.g = 5.60e-9*self.l2a(sec.diam) # end up as S/cm2
                seg.cm = 1.87e-11*self.l2a(sec.diam)*1e6 # end up as uF/cm2

    def make(self):
        self.topol()
        self.geom()
        self.biophys()
        
    def __str__(self):
        self.nnode = 50 #TODO why
        self.myL = 1000 #TODO why
        return "Cable with " + str(self.nnode) + " nodes, internode length of " + str(self.myL) + " microns"


h.celsius = 20

if __name__ == "__main__":
    mycable = Cable(nnode=50, myL=1000)  # appropriate down to 25um internode length
    print(mycable)
# hoc version of biophys procedure below:
"""
proc biophys() {local fac
    # ohm/cm must be converted to ohm-cm by multiplying by
    # cross sectional area
    fac = PI*diam^2/4 * 1e-8
    forall {
        Ra = 1.26e8 * fac
    }
    # paper relative to rest=0 but following values relative to -65
    forsec "node" {
        insert hh
        gnabar_hh = 1.2
        gkbar_hh = .09
        gl_hh = .02
        ena = 115 - 65
        ek = -12 - 65
        el_hh = -.05 - 65
        cm = 3.14e-9*l2a()*1e6 # end up as uF/cm2
    }
    forsec "myelin" {
        insert pas
        e_pas = -65
        g_pas = 5.60e-9*l2a() # end up as S/cm2
        cm = 1.87e-11*l2a()*1e6 # end up as uF/cm2
    }
}
"""