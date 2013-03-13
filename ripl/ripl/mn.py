"""Custom topologies for Mininet

author: Brandon Heller (brandonh@stanford.edu)

To use this file to run a RipL-specific topology on Mininet.  Example:

  sudo mn --custom ~/ripl/ripl/mn.py --topo ft,4
"""

from ripl.dctopo import FatTreeTopo #, VL2Topo, TreeTopo
from mininet.topo import SingleSwitchTopo
from jellyfish.topologies.jellyfish import JellyfishTopo

topos = { 'ft': FatTreeTopo, 'single' : SingleSwitchTopo, 'jelly' : JellyfishTopo}
#,
#          'vl2': VL2Topo,
#          'tree': TreeTopo }
