import math
import shlex
import sys
from subprocess import Popen
from time import sleep


def wait(msg, seconds, granularity=10):
  sys.stdout.write(msg)
  sys.stdout.flush()
  for i in range(granularity):
    sleep(float(seconds)/granularity)
    sys.stdout.write('.')
    sys.stdout.flush()
  print 'DONE'


def print_centered(msg, fill=' ', window_size=80):
  """ Prints the given message centered in the window.

  @param msg the message to print
  @param fill what to fill on either side of the message
  @param window_size the total size of the window
  """
  half = int((window_size - len(msg)) / 2)
  print fill * half + msg + fill * (window_size - half)


__colors = ['blue', 'red', 'green', 'coral', 'darkorange', 'brown',
            'darkolivegreen4', 'gold', 'deepskyblue', 'chartreuse',
            'aquamarine']


def _color_list(size):
  """ Returns a list of colors of length size."""
  return (__colors * (int(size / len(__colors)) + 1))[0:size]


def print_topo(topo, filename, paths=None):
  """ Use graphviz to draw the given topology.

  @param topo the Topo to print
  @param filename where to save the image and dot file
  @param paths an array of routes (arrays of nodes) to color
         (i.e. [['h1', 's1', 'h2'], ['h3', 'h4']])
  """
  print paths
  if not paths:
    paths = []
  path_edges = {}
  colors = _color_list(len(paths))
  for i in range(len(paths)):
    for j in range(len(paths[i]) - 1):
      key = (paths[i][j], paths[i][j+1])
      if key not in path_edges:
        path_edges[key] = []
      path_edges[key].append(colors[i])

  f = open("%s.dot" % filename, 'w')
  graph = topo.g

  f.write('graph G {\n')
  f.write('layout="neato";\n')

  switches = topo.switches()
  hosts = topo.hosts()
  nodes = switches + hosts
  num_switches = len(switches)

  for i in range(num_switches):
    x = math.cos(((math.pi*2)/num_switches)*i)*2
    y = math.sin(((math.pi*2)/num_switches)*i)*2
    f.write('%d[label="%s", pos="%s,%s!"];\n' % (i, switches[i], x, y))

  for i in range(len(hosts)):
    x = math.cos(((math.pi*2)/num_switches)*i)*3
    y = math.sin(((math.pi*2)/num_switches)*i)*3
    f.write('%d[label="%s", pos="%s,%s!"];\n' % (num_switches + i, hosts[i], x, y))

  for (u, v) in graph.edges_iter():
    c_string = ':'.join((path_edges[(u, v)] if (u, v) in path_edges else []) +
                        (path_edges[(v, u)] if (v, u) in path_edges else []))

    pos_u = nodes.index(u)
    pos_v = nodes.index(v)
    if c_string:
      f.write('%s -- %s [color="%s"];\n' % (pos_u, pos_v, c_string))
    else:
      f.write("%s -- %s\n" % (pos_u, pos_v))
  f.write('}')
  Popen(shlex.split('dot -Tpng -o%s.png %s.dot' % (filename, filename)))
