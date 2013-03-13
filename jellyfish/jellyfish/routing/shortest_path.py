#!/usr/bin/env python
"""@package routing

Routing for shortest path.

@author Patrick Costello (pcostell@stanford.edu)
@author Lynn Cuthriell (lcuth@stanford.edu)
"""
import Queue
import logging
from copy import deepcopy
import random
from ripl.routing import Routing


class KPathsRouting(Routing):

    def __init__(self, topo):
        '''Create Routing object.

        @param topo Topo object
        @param path_choice path choice function (see examples below)
        '''
        self.k = 8
        self.topo = topo
        random.seed()
        self.k_paths = dict()
        self.all_paths = dict()

    def k_shortest_paths(self, start, end):
      if (start, end) not in self.k_paths:
        self.k_paths[(start, end)]= self.find_all_paths(start, end)
      return self.k_paths[(start, end)]

    def find_all_paths(self, start, end):
      queue = Queue.Queue()
      first = [start]
      queue.put(first)
      all_paths = []

      while not queue.empty():
    
        path = queue.get()
        end_node = path[len(path)-1]
        if end_node == end:
          all_paths.append(path)
          if len(all_paths)==self.k:
            break

        up_edges = self.topo.up_edges(end_node)
        down_edges = self.topo.down_edges(end_node)
        all_edges = up_edges + down_edges
        for edge in all_edges:
          if not edge[1] in path:
            path_copy = deepcopy(path)
            path_copy.append(edge[1])
            queue.put(path_copy)
        
      return all_paths

    def get_route(self, src, dst, hash_):
      if src == dst:
        return [src]

      results = self.k_shortest_paths(src, dst)
      return sorted(results)[hash_ % len(results)]
