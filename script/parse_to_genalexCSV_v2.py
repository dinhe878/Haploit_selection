#!/usr/bin/env python

###############################################################################
# Author: Ding He                                                             #
# Email: dinghe6723@gmail.com                                                 #
#                                                                             #
# This script is for parsing a SLiM output (v2) to a GenAlEx csv file for     #
# further processes/analyses. The default is to parse all sperm haplotypes.   #
###############################################################################

import argparse

# a function to simplify processing SLiM output line by line
def processLine(splitLine, all_ind_haplotype_dict, all_haplotype, tag, gen):
    if tag != "all_tag":
        if gen != "all_gen": # specific generation with specific tag(s)
            for t in tag.split("_"):
                for g in gen.split("_"):
                    if t == splitLine[1] and g == splitLine[2]:
                        subpopID = splitLine[0] +"_"+ splitLine[1] +"_"+ splitLine[2]
                        ind_haplotype = splitLine[6].split(" ")
                        try:
                            all_ind_haplotype_dict[subpopID].append(ind_haplotype)
                        except:
                            all_ind_haplotype_dict[subpopID] = [ind_haplotype]
                        all_haplotype.update(ind_haplotype)
        else: # all generation with specific tag(s)
            for t in tag.split("_"):
                if t == splitLine[1]:
                    subpopID = splitLine[0] +"_"+ splitLine[1] +"_"+ splitLine[2]
                    ind_haplotype = splitLine[6].split(" ")
                    try:
                        all_ind_haplotype_dict[subpopID].append(ind_haplotype)
                    except:
                        all_ind_haplotype_dict[subpopID] = [ind_haplotype]
                    all_haplotype.update(ind_haplotype)

    else:
        if gen != "all_gen": # specific generation with all tag(s)
            for g in gen.split("_"):
                if g == splitLine[2]:
                    subpopID = splitLine[0] +"_"+ splitLine[1] +"_"+ splitLine[2]
                    ind_haplotype = splitLine[6].split(" ")
                    try:
                        all_ind_haplotype_dict[subpopID].append(ind_haplotype)
                    except:
                        all_ind_haplotype_dict[subpopID] = [ind_haplotype]
                    all_haplotype.update(ind_haplotype)
        else: # all generation with all tag(s)
            for t in tag.split("_"):
                if t == splitLine[1]:
                    subpopID = splitLine[0] +"_"+ splitLine[1] +"_"+ splitLine[2]
                    ind_haplotype = splitLine[6].split(" ")
                    try:
                        all_ind_haplotype_dict[subpopID].append(ind_haplotype)
                    except:
                        all_ind_haplotype_dict[subpopID] = [ind_haplotype]
                    all_haplotype.update(ind_haplotype)

    return

# parsing arguments from commandline
parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, help='input file should be a SLiM OUTPUT')
parser.add_argument('--gen', type=str, help='specify SLiM generation number(s) separated by underscores, or all generation')
parser.add_argument('--tag', type=str, help='specify individual tag number(s) separated by underscores, or all tags')
parser.add_argument('--parse_all', help='parse all records that include funding fathers and sperms', action='store_true')
parser.add_argument('--parse_fa', help='parse only funding fathers', action='store_true')

args = parser.parse_args()

inFile = open(args.i, 'r')
inFileName = args.i.split("/")[-1]
parse_option = "all_haplotypes" if args.parse_all else "sperm_haplotypes"
parse_option = "fa_haplotypes" if args.parse_fa else "sperm_haplotypes"
gen = args.gen if args.gen else "all_gen"
tag = args.tag if args.tag else "all_tag"
outFile = open(inFileName+"."+parse_option+".gen_"+gen+".tag_"+tag+".genalex.csv", 'w')

# a dictionary stores all the individual subpopID and haplotypes
all_ind_haplotype_dict = {}
# a set stores all the (unique) haplotypes in the population(s)
all_haplotype = set()

# process SLiM output line by line
print "reading input records..."
for line in inFile.readlines():
    lineToList = line.rstrip().split("|")

    # parse all records including all sperms and funding fathers
    if parse_option == "all_haplotypes":
        processLine(lineToList, all_ind_haplotype_dict, all_haplotype, tag, gen)
    # parse only funding fathers
    elif parse_option == "fa_haplotypes":
        if lineToList[0] == "M": processLine(lineToList, all_ind_haplotype_dict, all_haplotype, tag, gen)
    # [default] only parse all sperm records
    elif parse_option == "sperm_haplotypes":
        if lineToList[0] == "S": processLine(lineToList, all_ind_haplotype_dict, all_haplotype, tag, gen)

print "processing/writing records..."
# sort all haplotypes numerically
all_haplotype = map(str,sorted(map(int,all_haplotype)))
# make a flat list of all lists of individual haplotypes
all_ind_haplotype_list = []
for ind_haplotype_list in all_ind_haplotype_dict.values():
    for ind_haplotype in ind_haplotype_list:
        all_ind_haplotype_list.append(ind_haplotype)

# writing first three required lines for the GenAlEx format
outFile.write(str(len(all_haplotype)) + "," + str(len(all_ind_haplotype_list)) + "," + str(len(all_ind_haplotype_dict.keys())) + ","*len(all_haplotype)+"\n")
outFile.write(inFileName + ","*(len(all_haplotype)+2) + "\n")
outFile.write("ind,pop," + ",".join(all_haplotype) + "\n")

# convert haplotypes to binary strings 0/1 representing SNPs' absence/presnece, then write to outFile
ind_count = 1
# subpopID is sorted based on tag: M/S_tag_gen
for subpopID, ind_haplotype in sorted(all_ind_haplotype_dict.iteritems(), key=lambda x: int(x[0].split('_')[1])):
    for ind in ind_haplotype:
        binaryList = []
        for hap in all_haplotype:
            binaryList.append("1") if hap in ind else binaryList.append("0")

        outFile.write(str(ind_count) + "," + subpopID + "," + ",".join(binaryList) + "\n")
        ind_count += 1

outFile.close()
inFile.close()
