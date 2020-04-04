import sys
import re    

import default_commands

# Class that handles the special AVTS codes
# Child classes should overwrite the execute command only
class AVTSInterpreter:
    commands = {} # the commands -> (string: function)

    # Execute the ATVS command:
    def execute(self, avts, fullCommand):
        fullCommand = fullCommand.replace('\n', ' ').strip()
        reg = re.match(r"(\S+)\s+(.*)", fullCommand)
        if not reg:
            commandID = fullCommand
            args = ""
        else:
            commandID = reg.group(1)
            args = reg.group(2)
        if commandID in self.commands:
            v = self.commands[commandID](avts, args)
            if v: return v
            else: return ""
        else:
            return str(avts.evaluate(fullCommand))

    # Easy to use interface of command-setting (NOT modification):
    def setCommand(self, commstr, comm):
        if commstr not in self.commands:
            self.commands[commstr] = comm
            return True
        else: return False
    
class AVTS:
    # The main handler of the source. It reads the "next" input,
    # checks for special AVTS escape sequences, and gives instructions to the handlers.

    # Interpreter that handles the AVTS commands.
    # The interpreter of the AVTS should not be set or removed.
    interpreter = None

    # The input iterator. It is given during initialization. It can be changed anytime.
    # Examples: open(fname, 'r') or StringIO(txt)
    inputIter = None
    
    # Variables dictionary. Passed to "eval" as local variables.
    # Use the setVariable function to access it correctly
    vals = {}
    
    # Global variables/names dictionary. Passed to "eval" as globals.
    # By default, no python commands are allowed.
    # Use setEvalCommand function to access it correctly.
    # Only methods should be placed in global_vals.
    globalVals = {"__builtins__" : None}

    # Variable descriptions. Access it with the setVariableDescription function.
    variableDescriptions = {}

    # Stack of the environments. Acess the last element with the topEnv function.
    environmentStack = []
    
    # ------------------------------ Init ----------------------------------
    
    # Init with an input stream.
    def __init__(self, environment_in, inputIter_in):
        self.vals = {}
        self.globalVals = {}
        self.variableDescriptions = {}
        self.inputIter = inputIter_in
        self.interpreter = AVTSInterpreter()
        self.environmentStack = []
        self.environmentStack.append(environment_in)
        # fill the commands with default commands:
        self.interpreter.setCommand(self.topEnv().beginToken, default_commands.beginC)
        self.interpreter.setCommand(self.topEnv().recoverToken,default_commands.recoverC)
        self.interpreter.setCommand(self.topEnv().defToken, default_commands.defC)
        self.interpreter.setCommand(self.topEnv().resetToken, default_commands.resetC)
        # add a single "visible" variable to the variable stack:
        self.setEvalCommand("visible", lambda: self.topEnv().visible)
        
    # --------------------------- Modifiers --------------------------------

    # Variables values can NOT be overriden
    def setVariable(self, name, value):
        if name not in self.vals:
            self.vals[name] = value

    def setEvalCommand(self, name, command):
        self.globalVals[name] = command

    def setVariableDescription(self, name, desc):
        self.variableDescriptions[name] = desc

    def pushEnv(self, env):
        env.startContext()
        self.environmentStack.append(env)

    def popEnv(self):
        if len(self.environmentStack) == 1: return None
        self.environmentStack[-1].endContext()
        return self.environmentStack.pop()
        
    # ---------------------------  Getters ---------------------------------
    
    def topEnv(self):
        return self.environmentStack[-1]
    
    # --------------------------  Functions --------------------------------
    
    # Function to safely evaluate python expressions:
    def evaluate(self, python_expr):
        try:
            return eval(python_expr, self.globalVals, self.vals)
        except:
            raise Exception("Unable to evaluate python code: '" + python_expr + "'.")

    
    # The main component of the AVTS. Handles AVTS commands:
    do_collect = False
    collected = ""
   
    def _handle_inner(self, ns):#isLine = False)
        if not self.do_collect:
            reg = re.match(rf"(.*?){self.topEnv().startToken}(.*?)" +
                           rf"{self.topEnv().endToken}(.*)", ns)
            if reg:
                self.topEnv().print(reg.group(1))
                # Interpret:
                self.topEnv().print(self.interpreter.execute(self, reg.group(2) ))
                self._handle_inner(reg.group(3))
                return
            reg = re.match(rf"(.*?){self.topEnv().startToken}(.*)", ns)
            if not reg:
                self.topEnv().print(ns)
            else:
                self.topEnv().print(reg.group(1))
                self.do_collect = True
                self.collected += reg.group(2)
            return
        else: ## collecting: 
            reg = re.match(rf"(.*?){self.topEnv().endToken}(.*)", ns)
            if not reg:
                self.collected += ns
            else:
                self.collected += reg.group(1)
                self.do_collect = False
                # Interpret:
                self.topEnv().print(self.interpreter.execute(self, self.collected))
                self.collected = ""
                self._handle_inner(reg.group(2))
    
    def handle(self):
        # Iterate the input (supposedly: line by line)
        for ns in self.inputIter:
            ns = ns.strip("\n")
            reg = re.match(rf"\s*{self.topEnv().lineAVTSToken}(.*)", ns)
            if reg and not self.do_collect:
                self.interpreter.execute(self, reg.group(1))
            else :
                if self.do_collect == False:
                    self.topEnv().beginLine()
                self._handle_inner(ns)
                if self.do_collect == False:
                    self.topEnv().endLine()
    

# If AVTS is the main file => we execute it as a command-line file interpreter:
if __name__ == "__main__":
    import commandline_environment as textenv
    import _command_line
    sys.argv.pop(0)  # the name of this file: AVTS.py
    if (len(sys.argv) == 0 ) :
        sys.stderr.write('Error: Not enough arguments\n')
        exit(-1)
    env = textenv.TextEnvironment()
    vals = {} # accumulating the given variables
    restarg, masterfile, save_master = _command_line.parseArguments(sys.argv, vals)

    # end of switches: input file must come:
    inputfile = restarg.pop(0)
    f = open(inputfile, 'r')
    avts = AVTS(env, f)
    for k,v in vals.items():
        avts.setVariable(k, avts.evaluate(v))
        avts.setVariableDescription(k, "command line defined variable")

    #print("VALS: ", avts.vals)
    #print("GLOBALS: ", avts.globalVals)

    avts.handle()
    if save_master: _command_line.saveMaster(masterfile, inputfile, avts)
    
