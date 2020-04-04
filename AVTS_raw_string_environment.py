from AVTS_environment import *

class RawStringEnvironment(Environment) :
    def __init__(self, stream_in): #stream in is a lambda that gets a line as parameter
        self.stream = stream_in
    def printline(self, line):
        self.stream(line)
