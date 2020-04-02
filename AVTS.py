#!/usr/bin/env python3

# Adaptive Version Tracking System (AVTS)

helptext = u"""
\033[1mAdaptive Version Tracking System (AVTS)\033[m:
this system is a filter with higly tunable filtering rules.

\033[1mGeneral description\033[m
The logics of the filter is that the lines of the input file is printed according to the current environment. The environment depends on the application forum (eg. txt, pdf, html, etc.), and it has a lot of tunable parameters (for example visibility, text style, color, position, action on clicks, etc.). The environment can be changed by different context functions which maps an environment to an environment, and may depend on external user defined variables. The application of the context functions as well as the definition and use of the user defined varaibles can be changed by the AVTS directives.

The AVTS directives are contained by the input file. All directives are introduced by a remark sign (that can be #, % or //), followed by the AVTS keyword, then a command and the arguments.

\033[1mCurrently the available directives are\033[m:

\033[3m# AVTS def <variable> [= <value>] ["<description>"]\033[m: 
defines a variable, optionally assign an initial value to it, and give a description. The user defined variables are unmutable, and theirvalue comes from the FIRST occurance. The reason behind this rule is that the variables are first defined in the command line and later in the input file. Predefined variable is "current" which is used as the visibility variable of the current environment.

\033[3m# AVTS context <visibility bool>, <style description>\033[m: 
modifies the actual context. The visibility bool is a Python expression,which determines the visibility. The current visibility can be achived under the variable "current". The style description, which is a list of context functions, will act on the basic environment one after another, determining the current environment. The old context is pushed into a stack. All the variables occuring in the expressions or style descriptions must be defined earlier.

\033[3m# AVTS recover\033[m: 
restores the last environment from the stack

\033[3m# AVTS reset\033[m: 
resets the environment stack, and takes the basic environment.
The defined user variables can be set in the command line as well as in a master file.

\033[3m# AVTS replace\033[m: 
replaces the variable with its value transformed to string.
The defined user variables can be set in the command line as well as in a master file.

\033[1mUsage\033[m:
\033[3mAVTS.py <swiches> inputfile\033[m,

where the available switches are

\033[3m-help\033[m: prints this helptext
\033[3m-f masterfile\033[m: reads in the definitions of the variables from the masterfile. In this case the AVTS define directive may be omitted, if these are shown up already in the master file
\033[3m-save_master\033[m: the defined variables are saved in the master file. If no master file is given, we use the core input file name extended by "_AVTSmaster"
\033[3m-D <variable=value>\033[m: define a variable, and set its value

\033[1mExample\033[m:
Try the command python3 AVTS.py -D x=True basetext0.txt, and compare it with python3 AVTS.py -D x=False basetext0.txt. If you apply the -save_master switch, then all the defined variables are written out into a file, where it is easier to overview them.
"""

import sys
import re
import os.path
import copy

# the basic plain Environment class
# printline should be implemented in subclasses
# startContext/endContext will be executed when a new context is
# started/ended (context itself can change this function)
class Environment :
    visible = True
    def print(self, line) :
        if self.visible:
            self.printline(line)
    def printline(self, line) :
        print(line, end = '')
    def NoneOutput(self) :
        return None
    startContext = NoneOutput
    endContext = NoneOutput

    

# TextEnvironment:
# cf. https://en.wikipedia.org/wiki/ANSI_escape_code
class ANSIcode :
    reset = u"\033[m"
    bold = u"\033[1m"
    italic = u"\033[3m"
    underline = u"\033[4m"
    clear = u"\033[2J"
    
class TextEnvironment(Environment) :
    indent = ""
    modline = ""
    color = ""
    bgcolor = ""
    endline = ANSIcode.reset
    def printline(self, line) :
        print(self.bgcolor + self.color, end='')
        print(self.indent + self.modline, end='')
        print(line + self.endline, end='')

def Textsetcolor(r,g,b) :
    return u"\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def Textsetbgcolor(r,g,b) :
    return u"\033[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"


def remarkTextcommand(env_in) :
    env = copy.copy(env_in)
    env.modline = ANSIcode.italic
    env.color = Textsetcolor(120,120,120)
    env.indent = ">>>   "
    return env

remarkText = lambda env : remarkTextcommand(env)

def redTextcommand(env_in) :
    env = copy.copy(env_in)
    env.color = Textsetcolor(255,0,0)
    return env

redText = lambda env : redTextcommand(env)


def verboseOutputStart() :
    print(">>> Start context")

def verboseOutputEnd() :
    print(">>> End context")

def NoneOutput() :
    return None

def verboseTextcommand(env_in) :
    env = copy.copy(env_in)
    env.startContext = verboseOutputStart
    env.endContext = verboseOutputEnd
    return env

verboseText = lambda env : verboseTextcommand(env)

class LaTeXEnvironment(Environment) :
    def printline(self, line) :
        print(line, end = '')

# --------------------------------------------------------------------
# here starts the AVTS command parser
# --------------------------------------------------------------------

# global variable: the environment stack
stack = []

# the variable dictionary contains a single element for current visibility
dict ={"current" : "gives the visibility of the current environment"}
current =True

# interprets the current line as AVTS command.
# if it is not AVTS command, returns False
def AVTSinterpreter(line) :
    global stack
    AVTScommand = r'(.*)(#|//|%)\s*AVTS\s+(\w+)\s+(.*)$'
    m = re.match(AVTScommand, line)
    if not m :  # not AVTS command: use current environment to print line
        env = stack[-1]
        env.print(line)
        return ""
    if m.group(1) != '' :
        stack[-1].print( m.group(1) )
    if m.group(3) == 'def' : # it is a definition
        m1 = re.match(r'((\w+)\s*=\s*([\w\s]+))(\s+"([^"]*)\s*")?$', m.group(4))
        if m1.group(2) not in dict :
            dict.update( { m1.group(2) : m1.group(5)})
            return m1.group(1)
        else :
            dict[m1.group(2)] = m1.group(5)
            return ""
    if m.group(3) == 'context' :
        m1 = re.match(r'([^,]+)((,[^,]+)*)$', m.group(4))
        env = copy.copy(stack[-1])  # current environment is the last in the stack
        commands = m1.group(2).split(',')[1:] # read out contexts
        commands.reverse()
        for c in commands :
            env = eval(c)(env)
        env.visible = eval(m1.group(1))
        current = env.visible
        stack.append(env)
        env.startContext()
        return ""
    if m.group(3) == 'recover' :
        env = stack[-1]
        env.endContext()
        if(len(stack) > 1) : stack.pop()
        env = stack[-1]
        current = env.visible
        return ""
    if m.group(3) == 'reset' :
        while len(stack) > 1 :
            env = stack[-1]
            env.endContext()
            stack.pop()
        env = stack[-1]
        current = env.visible
        return ""
    if m.group(3) == 'replace' :
        env = stack[-1]
        env.print( str(eval(m.group(4))))
        return ""
    # if the line is AVTS command, but not interpretable:
    raise SyntaxError("in", line)


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
        m = re.match(r"((\w+)=([a-zA-Z0-9\" ]+))", opt)
        #print(opt, m.groups(), file = sys.stderr)
        toexec = toexec + m.group(1) +"\n"  # we treat each line as a python command!
        if m.group(2) not in dict :
            dict.update({m.group(2) : "command line defined variable"})
        continue
    print("Bad switch : ", opt, file = sys.stderr)
    exit(-1)

exec(toexec)

# here starts the evaluation of the actual file
basicEnvironment = TextEnvironment()
current = basicEnvironment.visible  # the current environment
stack.append(basicEnvironment)

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