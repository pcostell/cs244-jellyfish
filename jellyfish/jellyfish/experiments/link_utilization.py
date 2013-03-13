import operator
import random
from copy import deepcopy
def count_links(link_use, route):
  route.pop(0)
  if len(route) == 0:
    return
  route.pop()
  for i in range(0, len(route)-1):
    if 'h' in route[i] or 'h' in route[i+1]:
      continue
    link = (route[i], route[i+1])
    link_use[link]+=1


def calculate_link_utilization(topo, routing, routing_name, topo_name, result_dir):
  filename = '%s/link_util.txt' % result_dir
  print "outputing to %s" % filename
  f = open(filename, "w")
  f.write("%s %s\n" % (topo_name, routing_name))
  link_use = dict()
  for link in topo.links():
    if 'h' not in link[0] and 'h' not in link[1]:
      link_use[link] = 0
      link_use[link[::-1]] = 0

  random.seed()
  for num in range(100):
    for src in topo.hosts():
      for dst in topo.hosts():
        hash_ = random.getrandbits(32)
        route = deepcopy(routing.get_route(src, dst, hash_))
        count_links(link_use, route)
  sorted_l = sorted(link_use.iteritems(), key=operator.itemgetter(1))
  for i in range(len(sorted_l)):
    f.write(str(i)+" " + str(int(round(sorted_l[i][1]/100.0)))+'\n')

