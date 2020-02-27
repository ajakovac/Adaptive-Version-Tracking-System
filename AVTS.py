#!/usr/bin/env python3

# Adaptive Version Tracking System (AVTS)

helptext = """
Adaptive Version Tracking System (AVTS):
this system is a filter with higly tunable filtering rules.
The code works with two files, an input file and a master file. 
The input file can be any text file (including documentations,
program codes, etc.) containing AVTS switches, which define and tag 
blocks of the input file. The master file determines whether these blocks
appear in the output or not. For more information refer the documentation.

Usage:
python3 AVTS.py <swiches> inputfile <master file>

available switches:
-help : prints this helptext
-save_update : if there are tags in the input file that are missing
        from the master file, updates the master file accordingly
        The new items are as default unvisible

The input file is compulsory. The default for the master file is
the input file core (without extension) followed by "_AVTSmaster",
and no extension.
"""

import sys
import re
import os.path

AVTSid = r"(#|//)?\s*AVTS\s*([a-zA-Z]+)\s*({([^}]+)})?\s*$"
commands = ["begin", "end"]
# parses line to find AVTS directives
# returns False, None, None if it is a normal line
# returns True, commandtoken, id if it is AVTS line
def AVTSparse(line) :
    m = re.match(AVTSid, line)
    if (not m) :
        return False, None, None
    cmnd = m.group(2)
    if cmnd not in commands :
        print('bad command in ', line)
    return True, cmnd, m.group(4)

# collects variables in a boolean expression
def checkVariables(line) :
    return list(filter(lambda x : not re.match(r'^or|and$',x) and len(x)>0, 
                re.split(r"\W+",line)))

sys.argv.pop(0)  # the filename
if (len(sys.argv) == 0 ) :
    print('Not enough arguments')
    exit(-1)

# handles switches in the input line
save_master = False
optionhash = {}
masterfile = None

while (sys.argv[0])[0] == '-' :
    opt = sys.argv.pop(0)
    if (opt == '-help') :
        print(helptext)
        exit(0)
    if opt == '-save_master' :
        save_master = True
        continue
    m = re.match(r"-f", opt)
    if m :  # found a master file
        masterfile = sys.argv.pop(0)
        print("masterfile = ", masterfile, file = sys.stderr)
        try :
            f = open(masterfile)
            mastertext = f.read().splitlines()
            f.close()
        except IOError as err :
            print("IOError in master file: {0}".format(err))
        # create the option hash file from the master file
        IDpattern = r"\s*([^=\s]+)\s*=\s*(True|False)"
        for line in mastertext :
            if(len(line) == 0) : continue  # empty line
            if (line[0] == '#') : continue  # remark
            m = re.match(IDpattern, line)
            if(not m) :
                print("Bad format in master file : ", line)
            exec(m.group(0))  # we treat each line as a python command!
            if m.group(1) in optionhash :
                optionhash[m.group(1)] = bool(m.group(2))
            else :
                optionhash.update({m.group(1) : bool(m.group(2))})
        continue
    m = re.match(r"-T(\w+)", opt)
    if m :  # found a variable to set true
        exec(m.group(1) + "=True")
        if m.group(1) in optionhash :
            optionhash[m.group(1)] = True
        else :
            optionhash.update({m.group(1) : True})
        continue
    m = re.match(r"-F(\w+)", opt)
    if m :  # found a variable to set false
        exec(m.group(1) + "=False")
        if m.group(1) in optionhash :
            optionhash[m.group(1)] = False
        else :
            optionhash.update({m.group(1) : False})
        continue
    print("Bad switch : ", opt, file = sys.stderr)
    exit(-1)

# end of switches: input file must come
inputfile = sys.argv.pop(0)
try :
    f = open(inputfile)
    basetext = f.read().splitlines()
    f.close()
except IOError as err:
    print("IOError in input file: {0}".format(err))
    exit(-1)

# create option status
statusstack = [True]
visible = True  # we start with a visible status

# process the text according to the optionhash
for line in basetext :
    isAVTS, cmnid, boolexpr = AVTSparse(line)
    if (not isAVTS):
        if visible : print(line)
        continue
    if boolexpr is not None :
        varlist = checkVariables(boolexpr)
        for var in varlist :
            if var not in optionhash :
                optionhash.update({ var : False})
                exec( var + "= False")
            booleval = eval(boolexpr)
    else :  booleval = None
    if cmnid == "end" :
        visible = statusstack.pop()
        continue
    if cmnid == "begin" :
        if booleval is None :
            print("bad syntax in ", line)
            exit(-1)
        statusstack.append(visible)
        visible = booleval
        

# save master file if necessary
if save_master :
    if masterfile is None :
        m = re.match(r"(.*)\.[^.]+", inputfile)
        if m : masterfile = m.group(1) + "_master"
        else : masterfile = inputfile + "_master"
    f = open(masterfile, 'w')
    print("# AVTS master, automatic save", file = f)
    for i in optionhash :
        if optionhash[i] : print( i + " = True", file = f)
        else : print( i + " = False", file = f)
 