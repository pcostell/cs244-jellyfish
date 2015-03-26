#!/usr/bin/python

import os
from helper import *

output_file = 'throughput.txt'
result_dir = 'results/'
runs = {}
for name in os.listdir(result_dir):
  if os.path.isdir(os.path.join(result_dir, name)):
    name_s = name.split('-')
    topo = name_s[0]
    routing = name_s[1]
    flows = name_s[2]
    run = name_s[3]
    throughput_filename = '%s/%s/throughput.txt' % (result_dir, name)
    f = open(throughput_filename, 'r')
    throughput_percent = float(f.readline())
    if run not in runs:
      runs[run] = {}
    runs[run]['Topo: %s, Routing: %s, Flows: %s' % (topo, routing, flows)] = throughput_percent

of = file(output_file, 'w')
for k, v in runs.items():
  of.write('============ Run %s ==============\n' % k)
  for name, percent in v.items():
    of.write("%s ==> %0.2f%% of link bandwidth used. \n" % (name, percent * 100))
of.write('\n')
of.close()
