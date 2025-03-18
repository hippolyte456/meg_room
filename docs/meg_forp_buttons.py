""" Code to detect press event on the forp response keypads at the MEG/Neurospin
Attention: This only works on Linux (see the names of the parallel port) 

christophe@pallier.org & julie.bonnaire@outlook.fr
"""

from parallel import Parallel
from dataclasses import dataclass

@dataclass
class PortBit:
    port:int
    bit: int

# Each button is associated to a (parallel_port, bit)

mapping_buttons_parallelports = {  # Each button is associated to a (port, bit)         
'leftBlue': PortBit(2, 6),
'leftYellow': PortBit(0, 6),
'leftGreen': PortBit(0, 3),
'leftRed': PortBit(0, 4),
'rightBlue' :  PortBit(0, 5),
'rightYellow' : PortBit(1, 2),
'rightGreen' : PortBit(1, 5),
'rightRed' : PortBit(1, 4),
}

# Parallel port initialization
p0 = Parallel("/dev/parport0")
p1 = Parallel("/dev/parport1")
p2 = Parallel("/dev/parport2")
p3 = Parallel("/dev/parport3")  # a priori useless for response buttons


def get_buttons_state():
    inputs = [p0.PPRSTATUS(), p1.PPRSTATUS(), p2.PPRSTATUS(), p3.PPRSTATUS()]
    
    states = {}
    for button, a in mapping_buttons_parallelports.items():
        states[button] = inputs[a.port] &  2**a.bit == 2**a.bit
        
    return states
    

if __name__ == '__main__':
    while True: 
        print(get_buttons_state())



 	
 	
