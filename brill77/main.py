from neuron import h
h.load_file("stdrun.hoc")
h.load_file("nrngui.hoc") # load_file

import sys

h.dt = .025
h.steps_per_ms = 40
h.tstop = 10

print("Figures for Brill et. al, 1977")

figchoice = input("Enter 1, 2a, or 2b to request a figure: ")

if figchoice not in ['1','2a','2b']:
    sys.exit("Invalid figure chosen")
    
h.load_file(f"fig{figchoice}.hoc")
