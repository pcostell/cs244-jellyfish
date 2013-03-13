import random

from subprocess import Popen
from multiprocessing import Process

from jellyfish.result_creation.helper import read_list
from jellyfish.util import wait
from jellyfish.experiments.monitor import monitor_devs_ng

SAMPLE_WAIT_SEC = 10.0

def start_iperf_receiver(receiver, result_dir):
  receiver.popen("iperf-patched/src/iperf -s -w 16m -p 5001 > %s/%s-server.txt" % (result_dir, receiver), shell=True)


def start_iperf_sender(sender, receiver, flows, result_dir):
  print "Starting iperf from %s (%s) to %s (%s)." % (sender, sender.IP(), receiver, receiver.IP())
  sender.popen("iperf-patched/src/iperf -c %s -t 3600 -w 16m -p 5001 -f %d -i 1 -yc > %s/%s-client.txt" % (receiver.IP(), flows, result_dir, sender), shell=True)


def stop_iperf(node):
  node.popen("killall iperf")

def get_iface_for_host(host, topo):
  ups = topo.up_nodes(host)
  assert len(ups) == 1
  return "%s-eth%d" % (ups[0], topo.port(host, ups[0])[1])

def parse_rates(senders, topo, result_dir):
  ifaces = [get_iface_for_host(host, topo) for host in senders]
  print senders
  print ifaces
  data = read_list('%s/txrate.txt' % result_dir)
  total = 0.0
  n_samples = 0
  for row in data:
    try:
      ifname = row[1]
    except:
      continue
    if ifname in ifaces:
      total += (float(row[3]) * 8.0 / (1 << 20))
      n_samples += 1
  return total / n_samples

def start_throughput_experiment(net, topo, result_dir, bw, flows, time):
  #start_tcpprobe(result_dir)
  hosts = topo.hosts()
  random.shuffle(hosts)

  senders = hosts[0:len(hosts):2]
  receivers = hosts[1:len(hosts):2]

  if len(senders) != len(receivers):
    raise Exception('The number of hosts is odd. ')

  for receiver in receivers:
    start_iperf_receiver(net.getNodeByName(receiver), result_dir)
  wait('Waiting for iperf servers to start', 3)

  for (sender, receiver) in zip(senders, receivers):
    start_iperf_sender(net.getNodeByName(sender), net.getNodeByName(receiver), flows, result_dir)
  wait('Letting network warm up', SAMPLE_WAIT_SEC)

  monitor = Process(target=monitor_devs_ng,
                    args=('%s/txrate.txt' % result_dir, 0.01))
  monitor.start()

  wait ('Running experiment', time)

  monitor.terminate()

  wait('Stopping monitor', 2)

  for r in receivers:
    stop_iperf(net.getNodeByName(r))

  rate = parse_rates(senders, topo, result_dir)
  f = open('%s/throughput.txt' % result_dir, 'w')
  f.write('%s\n' % (rate / bw))
  f.close()
  print "The average sending rate is: %s" % rate
  print "The percent utilization is: %s" % (rate / bw)
