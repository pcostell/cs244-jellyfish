from helper import *
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sport', help="Enable the source port filter (Default is dest port)", action='store_true', dest="sport", default=False)
parser.add_argument('-o', '--out', dest="out", default=None)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)


"""
Sample line:
link_num times_used
"""

def parse_file(f):
    link_num = []
    use = []
    srtt = []
    legend = ''
    first_line = True
    for l in open(f).xreadlines():
        if first_line:
            legend = l
            first_line = False
            continue
        fields = l.strip().split(' ')
        link_num.append(fields[0])
        use.append(fields[1])
    return link_num, use, legend


def plot_cwnds(ax, files):
    points = {}
    for f in files:
        link_num, use, legend = parse_file(f)
        points[f]=([], legend.strip())
        for i in range(len(link_num)):
            points[f][0].append((link_num[i],int(use[i])))
            if i < len(link_num)-1 and int(use[i+1]) > int(use[i]):
              points[f][0].append((link_num[i+1], int(use[i])))
    return points


def plot(files):
    added = defaultdict(int)

    m.rc('figure', figsize=(6, 4))
    fig = plt.figure()
    plots = 1

    axPlot = fig.add_subplot(1, plots, 1)
    points = plot_cwnds(axPlot, files)
    for f in points.keys()[::-1]:
      axPlot.plot(first(points[f][0]), second(points[f][0]), lw=2, label=points[f][1])

    axPlot.legend(loc=2)
    axPlot.grid(True)
    axPlot.set_xlabel("Link rank")
    axPlot.set_ylabel("Number of times used")
    axPlot.set_title("Link utilization")

result_dir = 'results'
runs = {}
files = []
for name in os.listdir(result_dir):
  if os.path.isdir(os.path.join(result_dir, name)) and os.path.exists(os.path.join(result_dir, name, 'link_util.txt')):
    files.append('%s/%s/link_util.txt' % (result_dir, name))
plot(files)
if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()
