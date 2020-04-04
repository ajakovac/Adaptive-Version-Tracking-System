from environment import *

class ANSIcode :
    reset = u"\033[m"
    bold = u"\033[1m"
    italic = u"\033[3m"
    underline = u"\033[4m"
    clear = u"\033[2J"

def setColor(r,g,b) :
    return u"\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def setBGColor(r,g,b) :
    return u"\033[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

def remarkLambda(env):
    env.modline = ANSIcode.italic
    env.color = setColor(120,120,120)
    env.indent = ">>>   "

def verboseLambda(env):
    env.startContext = lambda : print(">>> Start context")
    env.endContext = lambda : print(">>> End context")

def red(env): env.color = setColor(255, 0, 0)
def green(env): env.color = setColor(0, 255, 0)
def blue(env): env.color = setColor(0, 0, 255)

def replaceSpaces(env): env.sep = '_'

class TextEnvironment(Environment) :
    indent = ""
    modline = ""
    color = ""
    bgcolor = ""
    ending = ANSIcode.reset
    sep = " "
    def beginLine(self) :
        if self.visible:
            self.print(self.indent)

    def __init__(self):
        self.setModder("red", red)
        self.setModder("green", green)
        self.setModder("blue", blue)
        self.setModder("remark", remarkLambda)
        self.setModder("verbose", verboseLambda)
        self.setModder("replaceSpaces", replaceSpaces)
    def output(self, inp):
        inp = str(inp)
        print(self.bgcolor + self.color, end='')
        print(self.modline, end='')
        print(inp.replace(" ", self.sep) + self.ending, end='')
