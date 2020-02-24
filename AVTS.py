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

remark = "#"
AVTSpattern = remark+r"?\s*AVTS\s*{([^}]+)}"
def AVTSparse(line) :
    m = re.match(AVTSpattern, line)
    if (not m) :
        return False, "", 0
    id = m.group(1)
    idlist = id.split(":")
    if (len(idlist) == 1) :
        level = 0
    elif (len(idlist) == 2) :
        id = idlist[0]
        level = int(idlist[1])
    else :
        print("corrupted AVTS ID in: " + line)
        exit(-3)
    return True, id, level

sys.argv.pop(0)
if (len(sys.argv) == 0 ) :
    print('Not enough arguments: base file is missing')
    exit(-1)

save_master = False
while (sys.argv[0])[0] == '-' :
    opt = sys.argv.pop(0)
    if (opt == '-help') :
        print(helptext)
        exit(0)
    if (opt == '-save_update') :
        save_master = True

inputfile = sys.argv.pop(0)
try :
    f = open(inputfile)
    basetext = f.read().splitlines()
    f.close()
except IOError as err:
    print("IOError in input file: {0}".format(err))
    exit(-1)

m = re.match(r"(.*)\.([^\.]*)", inputfile)
if m :  
    base = m.group(1)
    extension = m.group(2)
else :  
    base = inputfile
    extension = ""

AVTSmasterfile = None
if (len(sys.argv) == 0) :  # non explicit master file
    tryfile = base + "_AVTSmaster"
    if (os.path.isfile(tryfile)) :
        AVTSmasterfile = tryfile
else :
    AVTSmasterfile = sys.argv.pop(0)

if (AVTSmasterfile is not None) :
    try :
        f = open(AVTSmasterfile)
        mastertext = f.read().splitlines()
        f.close()
    except IOError as err :
        print("IOError in master file: {0}".format(err))
else :
    print("WARNING: No available AVTS master file found.", file=sys.stderr)
    print("To save changes use -save_update switch!", file=sys.stderr)
    AVTSmasterfile = base + "_AVTSmaster"
    mastertext = []

# create the option hash file from the master file
optionhash = {}
for line in mastertext :
    if(len(line) == 0) : continue  # empty line
    if (line[0] == '#') : continue  # remark
    llist = line.split(':')
    print(llist)
    optionhash.update({llist[0] : int(llist[1])})

# create option status
statushash = optionhash.copy()
for k in statushash :
    statushash[k] = False  # neither of the key were used

# process the text according to the optionhash
visible = True  # we start with a visible status

for line in basetext :
    isAVTS, id, level = AVTSparse(line)
    if (not isAVTS and visible) :
        print(line)
        continue
    idvalue = optionhash.get(id)
    if(idvalue is None) :  # tag is not in the master file
        optionhash.update({ id : -1 })  # restrictive mode
        statushash.update({ id : False })
        idvalue = -1
    if(statushash[id]) :
        statushash[id] = False
    else :  
        statushash[id] = True
    if(level != idvalue) :
        if(statushash[id]) : visible = False
        else : visible = True
 