
def def_endl(env):
    if env.visible:
        print("")

# Environment class that defines the behaviour of the ATVS interpreter:
class Environment:
    visible = True
    # Default printing function. NOT TO BE OVERRIDEN.
    def print(self, inp):
        if self.visible:
            self.output(inp)

    # Output is to be overriden
    def output(self, inp): print(inp, end='')

    startContext = lambda env: None
    endContext = lambda env: None
    beginLine = lambda env: None
    endLine = def_endl 
    
    # Tokens (must be regex compatible):
    startToken = "\$\(" # a ' ' should be placed after the startToken
    endToken = "\)\$" # any character can follow: eg: "##alma" is valid
    lineAVTSToken = "\$/"

    # Command tokens:
    beginToken = "begin"
    recoverToken = "end"
    defToken = "def"
    resetToken = "reset"

    modderList = dict()
    # comlambda : Environment -> Environment
    def setModder(self, m, mlambda):
        self.modderList[m] = mlambda

