#!/usr/bin/python

"CS244 Assignment 3: JellyFish"
import os
import random
import shlex
import shutil
import sys
from struct import pack
from subprocess import Popen, PIPE
from time import time
from zlib import crc32

from argparse import ArgumentParser
from mininet.link import TCLink
from mininet.log import lg
from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController, OVSSwitch
from mininet.util import dumpNodeConnections
from riplpox.util import getRouting, buildTopo, ROUTING

from jellyfish.util import print_topo, print_centered, wait
from ripl.mn import topos
from jellyfish.experiments.link_utilization import calculate_link_utilization
from jellyfish.experiments.throughput import start_throughput_experiment

# Parse arguments


parser = ArgumentParser(description="Jellyfish tests")
parser.add_argument('-t', '--topo',
                    dest="topo",
                    type=str,
                    action="store",
                    choices=[k for k, _ in topos.items()],
                    help="Topology to run.",
                    required=True)
parser.add_argument('--topo-args',
                    dest="topo_args",
                    type=str,
                    action="store",
                    help="Topology arguments, separted by comma. Can either be positional, or name based.",
                    required=False)
parser.add_argument('-r', '--routing',
                    dest="routing",
                    action="store",
                    choices=[k for k, _ in ROUTING.items()],
                    help="Routing protocol to use. One of kshortest or hashed.",
                    required=True)
parser.add_argument('--time',
                    dest="time",
                    action="store",
                    help="Time to run the experiment.",
                    type=float,
                    required=True)
parser.add_argument("-s", '--seed',
                    dest="seed",
                    action="store",
                    help="Seed for the random number generator. Allows the test to be reproducible.",
                    type=int,
                    default=0)
parser.add_argument('--dry',
                    dest="dry",
                    action="store_true",
                    help="If set, do not run the tests.",
                    default=False)
parser.add_argument('--pox-inline',
                    dest="pox_inline",
                    action="store_true",
                    help="If set, POX output will be inline as opposed to at the end of the tests.",
                    default=False)
parser.add_argument('--xterms',
                    dest="xterms",
                    action="store_true",
                    help="If set, mininet will open xterms for each host and switch.",
                    default=False)
parser.add_argument('--log-level',
                    dest="log_level",
                    action="store",
                    default='info',
                    help="Set the debug output level.")
parser.add_argument('--bw',
                    dest="bw",
                    action="store",
                    type=int,
                    default='10',
                    help='Bandwidth of links in Mbps.')
parser.add_argument('-e', '--experiment',
                    dest="experiment",
                    action='store',
                    type=str,
                    choices=['link_utilization', 'throughput'],
                    default='throughput',
                    help='The experiment to run.')
parser.add_argument('-f',
                    dest="flows",
                    action='store',
                    type=int,
                    default=1,
                    help="Number of flows to run between pairwise servers.")
args = parser.parse_args()

lg.setLogLevel(args.log_level)

def print_routes(topo, routing, filename):
  routes = []
  for h1 in topo.hosts():
    for h2 in topo.hosts():
      if h1 != h2:
        hosts =[h1, h2]
        routes.append(routing.get_route(h1, h2, crc32(pack('ss', *hosts))))
  print_topo(topo, filename, routes)

def main():
  "Create network and run Buffer Sizing experiment"
  start = time()
  random.seed(args.seed)
  # Reset to known state

  result_dir = "results/%s-%s-%s-%s" % (args.topo, args.routing, args.flows, args.seed)
  if not os.path.exists(result_dir):
    os.makedirs(result_dir)

  topo_all = args.topo + (",%s" % args.topo_args if args.topo_args else "")
  topo = buildTopo(topo_all, topos)
  print_topo(topo, '%s/%s' % (result_dir, args.topo), None)

  if args.experiment == 'link_utilization' and args.topo == 'jelly':
    routing_name = args.routing
    topo_name = args.topo
    if args.routing == 'kshortest':
      routing_name = '8 Shortest Paths'
    elif args.routing == 'hashed':
      routing_name = 'ECMP'
    if args.topo == 'jelly':
      topo_name = 'Jellyfish'
    elif args.topo == 'ft':
      topo_name = 'FatTree'
    if args.flows > 1:
      routing_name += " (%d flows)" % args.flows
    calculate_link_utilization(topo, getRouting(args.routing, topo), routing_name, topo_name, result_dir)
    end = time()
    print "Experiment took "+str(end - start)+" seconds."
    return
  if args.experiment == 'link_utilization':
    print "Experiment is a no-op."
    return


  pox_cmd = """python pox/pox.py --no-cli log --file=%s/pox.log,w riplpox.riplpox --topo=%s
    --routing=%s --mode=reactive"""
  pox_args = {
    "stdin" : PIPE,
    "stdout" : PIPE,
    "stderr" : PIPE
  } if not args.pox_inline else {}
  p = Popen(shlex.split(pox_cmd % (result_dir, topo_all, args.routing)), **pox_args)
  wait('Waiting for POX to start', 2)

  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, controller=RemoteController, autoSetMacs=True, xterms=args.xterms)
  net.start()

  dumpNodeConnections(net.hosts)

  if args.xterms:
    raw_input("Press enter to start experiments...")
  wait('Waiting for POX to sync', 20)
  #net.pingAll()

  if not args.dry:
    start_throughput_experiment(net, topo, result_dir, args.bw, args.flows, args.time);

  if args.xterms:
    raw_input("Press enter to kill everything...")
  net.stop()
  p.kill()
  #if not args.pox_inline:
  #  print_centered('POX Output', '=')
  #  print_centered('STDOUT', '+')
  #  print p.stdout.read()
  #  print_centered('STDERR', '+')
  #  print p.stderr.read()
  #  print_centered('POX Output Complete', '=')

  Popen("killall -9 top bwm-ng tcpdump cat mnexec tc", shell=True).wait()
  end = time()

  print "Experiment took "+str(end - start)+" seconds."


if __name__ == '__main__':
  print "Running Jellyfish with options:"
  for opt, value in vars(args).items():
    print "%s: %s" % (opt, value)
  try:
    main()
  except:
    print "-"*80
    print "Caught exception.  Cleaning up..."
    print "-"*80
    import traceback
    traceback.print_exc()
    os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")
