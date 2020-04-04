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
    beginLine = NoneOutput

    # Tokens: (must be regex compatible!!)
    AVTSStartToken = "\$\(" # a ' ' should be placed after the startToken
    AVTSEndToken = "\)\$" # any character can follow: eg: "##alma" is valid
    
    evalMarker = "\$\%" #must be written in the same word as the variable name: eg: $%x
    evalBeginMarker = "{"
    evalEndMarker = "}"

    # AVTS tokens:
    beginToken = "begin"
    recoverToken = "end"
    defToken = "def"
    resetToken = "reset"
    sepToken = ";"


class EnvironmentSkin:
    commands = dict()
    # comlambda : Environment -> Environment
    def setCommand(self, com, comlambda):
        self.commands[com] = comlambda

