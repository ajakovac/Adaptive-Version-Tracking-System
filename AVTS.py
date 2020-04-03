#!/usr/bin/env python3

# Adaptive Version Tracking System (AVTS)

import sys
import re
import os.path
import copy

from AVTS_environment import *

class AVTS:
    throw_exception = False

    def __init__(self, env, skin_in):
        self.stack = []
        self.stack.append(env)
        self.vals ={"current" : [True, "gives the visibility of the current environment"]}
        self.skin = skin_in
        self.variables = {}

    def setVariableFromExpression(self, name, expression, desc = ""):
        try:
            for k, v in self.vals.items():
                exec(k + "=" + str(v[0]))
            exec(expression)
            if desc == "":
                if name in self.vals: #don't replace the description
                    self.vals[name][0] = eval(name)
                else: # add default description:
                    self.vals[name] = [eval(name), "no description"]
            else: #if the description is given:
                self.vals[name] = [eval(name), desc]
        except:
            raise Exception("Unable to set variable '" + name + "' from expression '" + expr + "'.")

    def setVariable(self, name, value, desc = ""):
        try:
            if desc == "":
                if name in self.vals: #don't replace the description
                    self.vals[name][0] = value
                else: # add default description:
                    self.vals[name] = [value, "no description"]
            else: #if the description is given:
                self.vals[name] = [value, desc]
        except:
            raise Exception("Unable to set variable '" + name+ " to value '" + value + "'.")
            
    def removeVariable(self, name):
        self.vals.pop(name)        

    def getOuterEnvironment(self):
        return self.stack[0]
        
    def interpret(self, fname):
        try :
            f = open(fname)
            for line in f :
                self.interpretLine(line)
            f.close()
            return True
        except IOError as err:
            stack[-1].print("IOError in input file: {0}".format(err))
            return False
        
    # interprets the current line as AVTS command.
    # if it is not AVTS command, returns False
    def interpretLine(self, line) :
        # global stack
        AVTScommand = r'(.*)(#|//|%)\s*AVTS\s+(\w+)\s+(.*)$'
        m = re.match(AVTScommand, line)
        if not m :  # not AVTS command: use current environment to print line
            env = self.stack[-1]
            env.print(line)
            return
        if m.group(1) != '' :
            self.stack[-1].print( m.group(1) )
        if m.group(3) == 'def' : # it is a definition
            m1 = re.match(r'((\w+)\s*=\s*([\w\s]+))(\s+"([^"]*)\s*")?$', m.group(4))
            if m1.group(2) not in self.vals :
                self.setVariableFromExpression(m1.group(2), m1.group(1), m1.group(5))
            else :
                (self.vals[m1.group(2)])[1] = m1.group(5)
            return
        if m.group(3) == 'context' :
            m1 = re.match(r'([^,]+)((,[^,]+)*)$', m.group(4))
            env = copy.copy(self.stack[-1])  # current environment is the last in the stack
            # read out contexts:
            commands = list(map(lambda x: x.strip(), m1.group(2).split(',')[1:]) )
            commands.reverse()
            for c in commands :
                lamb = self.skin.commands.get(c, "NULL")
                if lamb != "NULL":
                    env = lamb(env)
                elif self.throw_exception:
                    raise Exception("Invalid Context Command") # javítani
                else:
                    env.print("<UNKNOWN COMMAND: " + c + ">")
            for k, v in self.vals.items():
                exec(k + "=" + str(v[0]))
            env.visible = eval(m1.group(1)) # variable
            self.vals["current"][0] = env.visible
            self.stack.append(env)
            env.startContext()
            return
        if m.group(3) == 'recover' :
            env = self.stack[-1]
            env.endContext()
            if(len(self.stack) > 1) : self.stack.pop()
            env = self.stack[-1]
            self.current = env.visible
            return
        if m.group(3) == 'reset' :
            while len(self.stack) > 1 :
                env = self.stack[-1]
                env.endContext()
                self.stack.pop()
            env = self.stack[-1]
            self.current = env.visible
            return
        if m.group(3) == 'replace' :
            env = self.stack[-1]
            for k, v in self.vals.items():
                exec(k + "=" + str(v[0]))
            env.print( str(eval(m.group(4))))
            return
        # if the line is AVTS command, but not interpretable:
        if self.throw_exception:
            raise SyntaxError("in", line)
        else:
            self.stack[-1].print("<SYNTAX ERROR: " + line + ">")

