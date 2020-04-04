from AVTS_environment import *

import copy

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
    sep = " "
    beginLine = lambda self: self.print(self.indent)
    def printline(self, line) :
        print(self.bgcolor + self.color, end='')
        print(self.modline, end='')
        print(line.replace(" ", self.sep) + self.endline, end='')

def setcolor(r,g,b) :
    return u"\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def setbgcolor(r,g,b) :
    return u"\033[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def remark(env_in) :
    env = copy.copy(env_in)
    env.modline = ANSIcode.italic
    env.color = setcolor(120,120,120)
    env.indent = ">>>   "
    return env

#remark = lambda env : remarkcommand(env)

def red(env_in) :
    env = copy.copy(env_in)
    env.color = setcolor(255,0,0)
    return env

def replaceSpaces(env_in) :
    env = copy.copy(env_in)
    env.sep = "_"
    return env

#red = lambda env : redcommand(env)

def verboseOutputStart() :
    print(">>> Start context")

def verboseOutputEnd() :
    print(">>> End context")

def NoneOutput() :
    return None

def verbose(env_in) :
    env = copy.copy(env_in)
    env.startContext = verboseOutputStart
    env.endContext = verboseOutputEnd
    return env

#verbose = lambda env : verbosecommand(env)
def defaultSkin():
    defaultSkinvar = EnvironmentSkin()
    defaultSkinvar.setCommand("remark", remark)
    defaultSkinvar.setCommand("verbose", verbose)
    defaultSkinvar.setCommand("red", red)
    defaultSkinvar.setCommand("replaceSpaces", replaceSpaces)
    return defaultSkinvar
