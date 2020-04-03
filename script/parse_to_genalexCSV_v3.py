#!/usr/bin/env python

###############################################################################
# Author: Ding He                                                             #
# Email: dinghe6723@gmail.com                                                 #
#                                                                             #
# This script is for parsing a SLiM output (v3, nucleotide-enabled version)   #
# to a GenAlEx csv file for further processes/analyses. The default is to     #
# parse all sperm haplotypes.                                                 #
#                                                                             #
# Note: nucleotide code in SLiM (A=0, C=1, G=2, T=3) is different from the    #
# default code in GenAlEx (A=1, C=2, G=3, T=4, 5=other)                       #
###############################################################################

import argparse

# a function to processing splited lines from SLiM output
def processRecord(splitLine, all_ind_haplotype_dict, all_haplotype):
    subpopID = splitLine[0] +"_"+ splitLine[1] +"_"+ splitLine[2]
    ind_haplotype_pos = splitLine[7].split(" ")
    ind_haplotype_value = splitLine[8].split(" ")

    # store {pos:value}
    ind_haplotype_dict = {}
    for i in range(0,len(ind_haplotype_pos)):
        ind_haplotype_dict[ind_haplotype_pos[i]] = ind_haplotype_value[i]

    try:
        all_ind_haplotype_dict[subpopID].append(ind_haplotype_dict)
    except:
        all_ind_haplotype_dict[subpopID] = [ind_haplotype_dict]

    all_haplotype.update(ind_haplotype_pos)

# a function to processing SLiM output line by line based on some commandline options
def processLine(splitLine, all_ind_haplotype_dict, all_haplotype, tag, gen):
    if tag != "all_tag":
        # specific generation(s) with specific tag(s)
        if gen != "all_gen":
            for t in tag.split("_"):
                for g in gen.split("_"):
                    if t == splitLine[1] and g == splitLine[2]:
                        processRecord(splitLine, all_ind_haplotype_dict, all_haplotype)
        # all generations with specific tag(s)
        else:
            for t in tag.split("_"):
                if t == splitLine[1]:
                    processRecord(splitLine, all_ind_haplotype_dict, all_haplotype)
    else:
        # specific generation(s) with all tags
        if gen != "all_gen":
            for g in gen.split("_"):
                if g == splitLine[2]:
                    processRecord(splitLine, all_ind_haplotype_dict, all_haplotype)
        # all generations with all tags
        else:
            processRecord(splitLine, all_ind_haplotype_dict, all_haplotype)

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

# a dictionary stores all the individual subpopID and haplotypes: {subpopID: [{ind_haplotype_pos[i]: ind_haplotype_value[i]},...]}
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
# make a flat list of all lists of individual haplotype dictionary
all_ind_haplotype_dict_list = []
for ind_haplotype_dict_list in all_ind_haplotype_dict.values():
    for ind_haplotype_dict in ind_haplotype_dict_list:
        all_ind_haplotype_dict_list.append(ind_haplotype_dict)

# writing first three required lines for the GenAlEx format
outFile.write(str(len(all_haplotype)) + "," + str(len(all_ind_haplotype_dict_list)) + "," + str(len(all_ind_haplotype_dict.keys())) + ","*len(all_haplotype)+"\n")
outFile.write(inFileName + ","*(len(all_haplotype)+2) + "\n")
outFile.write("ind,pop," + ",".join(all_haplotype) + "\n")

# convert haplotypes to a SNP matrix then write to outFile
ind_count = 1
# subpopID is sorted based on tag: M/S_tag_gen
for subpopID, ind_haplotype_dict_list in sorted(all_ind_haplotype_dict.iteritems(), key=lambda x: int(x[0].split('_')[1])):
    print
    for ind_haplotype_dict in ind_haplotype_dict_list:
        nucleotideCodeList = []
        for hap in all_haplotype:
            try:
                nucleotideCodeList.append(str(int(ind_haplotype_dict[hap])+1)) # note: SLiM code converts to GenAlEx code
            except:
                nucleotideCodeList.append("5") # here "5" represent ancestral state

        outFile.write(str(ind_count) + "," + subpopID + "," + ",".join(nucleotideCodeList) + "\n")
        ind_count += 1

outFile.close()
inFile.close()
