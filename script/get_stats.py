#!/usr/bin/env python

###############################################################################
# Author: Ding He                                                             #
# Email: dinghe6723@gmail.com                                                 #
#                                                                             #
# This script calculate some statistics from a SLiM output                    #
###############################################################################

import argparse

# parsing arguments from commandline
parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, help='input file should be a SLiM OUTPUT')
args = parser.parse_args()
inFile = open(args.i, 'r')

# count all tags which uniquly trace back to the original funding fathers
all_tags_dict = {}

# processing line by line
for line in inFile.readlines():
    try:
        all_tags_dict["tag_"+line.rstrip().split("|")[1]] += 1
    except:
        all_tags_dict["tag_"+line.rstrip().split("|")[1]] = 1

# print numbers and a simple terminal bar-like chart
dataForBarChart = {}
for tag, count in sorted(all_tags_dict.iteritems(), key=lambda x: x[1]):
    sperm_subpop_count = count/1000
    print tag, ": ", sperm_subpop_count, " within-ejaculate sperm population"
    try:
        dataForBarChart[sperm_subpop_count] += 1
    except:
        dataForBarChart[sperm_subpop_count] = 1

for k, v in sorted(dataForBarChart.iteritems()):
    bar = "*" * v
    print "sperm subpop count:" + str(k).rjust(5) + " |" + str(v).rjust(5) + " " + bar
