from environment import *

class RawEnvironment(Environment) :
    def beginLine(self) :
        if self.visible:
            self.print(self.indent)

    def __init__(self, stream_in, begl_in, endl_in):
        self.stream = stream_in
        self.beginL = begl_in
        self.endL = endl_in
        
    def output(self, inp):
        self.stream(inp)

    def beginLine(self):
        self.beginL()

    def endLine(self):
        self.endL()
