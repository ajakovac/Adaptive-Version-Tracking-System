#!/usr/bin/env python3

# Adaptive Version Tracking System (AVTS)

helptext = """
Adaptive Version Tracking System (AVTS):
this system is a filter with higly tunable filtering rules.

The logics of the filter is that the lines of the input file is printed
according to the current environment. The environment depends on the 
application forum (eg. txt, pdf, html, etc.), and it has a lot of tunable
parameters (for example visibility, text style, color, position, action
on clicks, etc.). The environment can be changed by different 
context functions which maps an environment to an environment, and my 
depend on external user defined variables. The application of the
context functions as well as the definition and use of the user defined
varaibles can be changed by the AVTS directives.

The AVTS directives are contained by the input file. All directives are
introduced by a remark sign (that can be #, % or //), followed by
the AVTS keyword, then a command and the arguments in curly brackets.
Currently the available directives are:

# AVTS def <variable> [= <value>] ["<description>"]
defines a variable, optionally assign an initial value to it, and give
a description. The user defined variables are unmutable, and their
value comes from the FIRST occurance. The reason behind this rule is that
the variables are first defined in the command line and later in the
input file. Predefined variable is "current" which is used as the
visibility variable of the current environment.

# AVTS context <visibility bool>, <style description>
modifies the actual context. The visibility bool is a Python expression,
which determines the visibility. The current visibility can be achived 
under the variable "current". The style description, which is a list
of context functions, will act on the basic environment one after another,
determining the current environment. The old context is pushed into a stack.
All the variables occuring in the expressions or style descriptions 
must be defined earlier.

# AVTS recover
restores the last environment from the stack

# AVTS reset
resets the environment stack, and takes the basic environment.

The defined user variables can be set in the command line as well as
in a master file. 

Usage:
AVTS.py <swiches> inputfile

available switches:
-help : prints this helptext
- f masterfile: reads in the definitions of the variables from 
the masterfile. In this case the AVTS define directive may be omitted,
if these are shown up already in the master file
-save_update : the defined variables are saved in the master file. If 
no master file is given, we use the core input file name extended by
"_AVTSmaster"
-D<variable=value> : define a variable, and set its value

"""

import sys
import re
import os.path
import copy

# cf. https://en.wikipedia.org/wiki/ANSI_escape_code
# these are the environment modifying contexts
def setcolor(r,g,b) :
    return u"\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def setbgcolor(r,g,b) :
    return u"\033[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

class ANSIcode :
    reset = u"\033[m"
    bold = u"\033[1m"
    italic = u"\033[3m"
    underline = u"\033[4m"
    clear = u"\033[2J"

# the current lines are printed according to the actual Environment
class Environment :
    visible = True
    indent = ""
    modline = ""
    color = setcolor(0,0,0)
    def str(self) :
        return(self.modline)
    def print(self, line) :
        if self.visible : 
            print(self.indent + self.modline + self.color + line + ANSIcode.reset, end='')

def mainTextcommand(env_in) :
    return Environment()

mainText = lambda env : mainTextcommand(env)

def remarkTextcommand(env_in) :
    env = copy.copy(env_in)
    env.modline = ANSIcode.italic
    env.color = setcolor(120,120,120)
    env.indent = "   "
    return env

remarkText = lambda env : remarkTextcommand(env)

def redTextcommand(env_in) :
    env = copy.copy(env_in)
    env.color = setcolor(255,0,0)
    return env

redText = lambda env : redTextcommand(env)


# here starts the AVTS command parser
dict ={"current" : "gives the visibility of the current environment"}
current =True
basicEnvironment = Environment()
current = basicEnvironment.visible  # the current environment
stack = [basicEnvironment]

# interprets the current line as AVTS command.
# if it is not AVTS command, returns False
def AVTSinterpreter(line) :
    global stack
    AVTSdef = r'(#|//)?\s*AVTS\s+def\s+((\w+)\s*=\s*([\w\s]+))(\s+"([^"]*)\s*")?$'
    m = re.match(AVTSdef, line)
    if m : # it is a definition
        if m.group(3) not in dict :
            dict.update( { m.group(3) : m.group(6)})
            return m.group(2)
        else :
            dict[m.group(3)] = m.group(6)
            return ""
    AVTScontext = r'(#|//)?\s*AVTS\s+context\s+([^,]+)((,[^,]+)*)$'
    m = re.match(AVTScontext, line)
    if m : # context change command
        env = copy.copy(stack[-1])  # current environment is the last in the stack
        commands = m.group(3).split(',')[1:] # read out contexts
        commands.reverse()
        for c in commands :
            env = eval(c)(env)
        env.visible = eval(m.group(2))
        current = env.visible
        stack.append(env)
        return ""
    AVTSrecover = r'(#|//)?\s*AVTS\s+recover\s*$'
    m = re.match(AVTSrecover, line)
    if m :
        stack.pop()
        env = stack[-1]
        current = env.visible
        return ""
    AVTSreset = r'(#|//)?\s*AVTS\s+reset\s*$'
    m = re.match(AVTSreset, line)
    if m :
        env = stack[0]
        stack = [basicEnvironment]
        current = env.visible
        return ""
    # not AVTS command: to be printed
    env = stack[-1]
    env.print(line)
    return ""


sys.argv.pop(0)  # the filename
if (len(sys.argv) == 0 ) :
    print('Not enough arguments')
    exit(-1)

# handles switches in the input line
save_master = False
masterfile = None
toexec = ""

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
        IDpattern = r'\s*((\w+)\s*=\s*([^"]+))(\s+"([^"]*)")?$'
        for line in mastertext :
            if(len(line) == 0) : continue  # empty line
            if (line[0] == '#') : continue  # remark
            m = re.match(IDpattern, line)
            if(not m) :
                print("Bad format in master file : ", line)
            toexec = toexec + m.group(1) +"\n"  # we treat each line as a python command!
            if m.group(2) not in dict :
                dict.update({m.group(2) : m.group(5) })
            else :
                dict[m.group(2)] = m.group(5)
        continue
    m = re.match(r"-D", opt)
    if m :  # found a variable to be defined
        opt = sys.argv.pop(0)
        m = re.match(r"((\w+)=(\w+))", opt)
        toexec = toexec + m.group(1) +"\n"  # we treat each line as a python command!
        if m.group(2) not in dict :
            dict.update({m.group(2) : "command line defined variable"})
        continue
    print("Bad switch : ", opt, file = sys.stderr)
    exit(-1)

exec(toexec)

# end of switches: input file must come
inputfile = sys.argv.pop(0)
try :
    f = open(inputfile)
    for line in f :
        exec(AVTSinterpreter(line))
    f.close()
except IOError as err:
    print("IOError in input file: {0}".format(err))
    exit(-1)

# save master file if necessary
if save_master :
    if masterfile is None :
        m = re.match(r"(.*)\.[^.]+", inputfile)
        if m : masterfile = m.group(1) + "_master"
        else : masterfile = inputfile + "_master"
    f = open(masterfile, 'w')
    print("# AVTS master, automatic save", file = f)
    for i in dict :
        print(i +"="+ str(eval(i)) +' "' + dict[i] +'"', file = f)
    f.close()