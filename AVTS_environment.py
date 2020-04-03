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

class EnvironmentSkin:
    commands = dict()
    # comlambda : Environment -> Environment
    def setCommand(self, com, comlambda):
        self.commands[com] = comlambda

