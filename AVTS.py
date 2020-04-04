#!/usr/bin/env python3

# Adaptive Version Tracking System (AVTS)

import sys
import re
import os.path
import copy

from AVTS_environment import *

# The global parameters passed to ALL eval statements:
safe_globals = {
    # No built-in functions are enabled, unless specified otherwise:
    "__builtins__" : None
}

class ContextHandler:
    ID = "BASE"
    def __init__(self, avts_in):
        self.avts = avts_in
    def start(self, env): pass
    def handle(self, env, word, ws = ""): pass
    def end(self, env): pass

class NormalContext(ContextHandler):
    ID = "normal"
    def start(self, env): pass
    def handle(self, env, word, ws = ""):
        reg = re.match(rf"(.*){env.AVTSStartToken}(.*)", word)
        if reg: # -- start token --
            if ws != "": env.print(ws)
            if reg.group(1) != "": env.print(reg.group(1))
            self.avts.addContextType("AVTS", reg.group(2))
        else:
            if ws != "": env.print(ws)
            if word != "": env.print(word)

    def end(self, env): pass

class EvalContext(ContextHandler):
    ID = "eval"
    expression = ""
    def start(self, env):
        self.expression = ""
    def handle(self, env, word, ws = ""):
        reg = re.match(rf"(.*){env.evalEndMarker}(.*)", word)
        if not reg:
            self.expression += word
        else: # if the eval end marker is detected:
            self.expression += reg.group(1)
            # remove the "eval" context type from avts:
            self.avts.removeContextType(reg.group(2)) # sending overlapping word back...
            self.avts.interpretString(str(eval(self.expression,
                                               safe_globals,
                                               self.avts.vals)))
    def end(self, env): pass

class AVTSContext(ContextHandler):
    ID = "AVTS"
    def start(self, env): pass
    def handle(self, env, word, ws = ""):
        if word.strip() == "": return
        reg = re.match(rf"(.*)({env.AVTSEndToken})(.*)", word)
        if reg: # This can only happen if the whole AVTS command is one word
            self.handle(env, reg.group(1))
            self.avts.interpretWord(reg.group(2)+reg.group(3), "")
            return
        # Handling separators:
        reg = re.match(rf"(.*){env.sepToken}(.*)", word)
        if reg: # if a separator is found (aka if there are seperators in this WORD):
            self.handle(env, reg.group(1))
            self.handle(env, reg.group(2))
            return
        # If there are no separators:
        if word == env.beginToken:     # begin token
            self.avts.addContextType("AVTS begin", "") # no overlapping word
            return
        elif word == env.defToken: # def token
            self.avts.addContextType("AVTS def", "") # no overlapping word
            return
        elif word == env.recoverToken: # recover token
            if len(self.avts.stack) > 1:
                env.endContext()
                self.avts.stack.pop() # pop environment
        elif word == env.resetToken: # reset token
            while len(self.avts.stack) > 1 :
                en = self.avts.stack[-1]
                en.endContext()
                self.avts.stack.pop()
        else: # Invalid syntax
            if self.avts.throw_exception:
                raise Exception("Invalid AVTS command: " + word + ".")
            else:
                env.print("<UNKNOWN AVTS COMMAND: " + word + ">\n")
    def end(self, env): pass
    
class AVTSbeginContext(ContextHandler):
    ID = "AVTS begin"
    lambda_list = []
    before_first_comma = True
    expression = ""
    def start(self, env):
        self.before_first_comma = True
        # resetting the labda list:
        self.lambda_list = []
        self.expression = ""
        
    # NOTE: it is guaranteed, that there is no AVTSEndToken in "word"
    def handle(self, env, word, ws = ""):
        if word.strip() == "": return
        reg = re.match(rf"(.*){env.sepToken}(.*)", word)
        if reg:
            self.handle(env, reg.group(1), "")
            self.avts.removeContextType(reg.group(2))
            return        
        reg = re.match(rf"(.*),(.*)", word)
        # If there is a comma in the word:
        if reg:
            self.handle(env, reg.group(1))
            # Evaluate the expression before the first comma:
            self.before_first_comma = False
            self.handle(env, reg.group(2))
            return
        # At this point, we have no commas in the word    
        # Handling the first expression, that is evaluated to a boolean:
        if self.before_first_comma:
            self.expression += word
        else: # After the first comma, we have a list of lambdas.
            self.lambda_list.append(word.strip()) # note: removing whitespaces

    def end(self, env):
        newenv = copy.copy(env)
        # evaluating the context-visibility-descipting booloean:
        newenv.visible = eval(self.expression, safe_globals, self.avts.vals) # variable
        self.avts.vals["current"] = newenv.visible
        newenv.startContext()
        # Evaluating all the lambda expressions, backwards:
        self.lambda_list.reverse()
        for l in self.lambda_list:
            lamb = self.avts.skin.commands.get(l, "NULL")
            if lamb != "NULL":
                newenv = lamb(newenv)
            elif self.avts.throw_exception:
                raise Exception("Invalid Context Command") # javítani
            else:
                newenv.print("<UNKNOWN STYLE COMMAND: " + l + ">\n")
        self.avts.stack.append(newenv)

class AVTSdefContext(ContextHandler):
    ID = "AVTS def"
    before_first_comma = True
    before_first_equal_sign = True
    var_name = ""
    expression = ""
    description = ""
    def start(self, env):
        self.before_first_comma = True
        self.before_first_equal_sign = True
        self.expression = ""
        self.description = ""
        self.var_name = ""

    def handle(self, env, word, ws = ""):
        reg = re.match(rf"(.*){env.sepToken}(.*)", word)
        if reg:
            self.handle(env, reg.group(1), "")
            self.avts.removeContextType(reg.group(2))
            return        
        if word.strip() == "": return
        if self.before_first_comma:
            reg = re.match(rf"(.*),(.*)", word)
            # If there is a comma in the word:
            if reg:
                self.handle(env, reg.group(1))
                # Evaluate the expression before the first comma:
                self.before_first_comma = False
                self.handle(env, reg.group(2))
                return
            # no commas in the word:
            reg1 = re.match(rf"(.*)=(.*)", word)
            if reg1:
                if (self.var_name == ""):
                    self.var_name = reg1.group(1)
                elif reg1.group(1) != "":
                    if self.avts.throw_exception:
                        raise Exception("Variable contains space: '" + self.var_name +
                                        " " + reg1.group(1) + "'")
                    else:
                        env.print("<INVALID VARIABLE NAME: '" + self.var_name +
                                        " " + reg1.group(1) + "'>")
                        return
                self.expression = reg1.group(2)
                self.before_first_equal_sign = False
                return
            if self.before_first_equal_sign:
                if self.var_name != "":
                    if self.avts.throw_exception:
                        raise Exception("Variable contains space: '" + self.var_name +
                                        " " + reg1.group(1) + "'")
                    else:
                        env.print("<INVALID VARIABLE NAME: '" + self.var_name +
                                  " " + reg1.group(1) + "'>")
                        return
                self.var_name = word
            else:
                self.expression += word + " "
        else:
            self.description += word + " "

    def end(self, env):
        self.avts.setVariable(self.var_name, 
                              eval(self.expression, safe_globals, self.avts.vals),
                              self.description)
        
class AVTS:
    throw_exception = False

    def __init__(self, env, skin_in):
        self.stack = []
        self.stack.append(env)
        self.vals ={"current" : True}
        self.valsDesc = {"current": "gives the visibility of the current environment"}
        self.skin = skin_in
        self.variables = {}

        self.handlers = {
            "normal" : NormalContext(self),
            "eval" : EvalContext(self),
            "AVTS" : AVTSContext(self),
            "AVTS def" : AVTSdefContext(self),
            "AVTS begin" : AVTSbeginContext(self)
            }

    def setVariable(self, name, value, desc = None):
        # setting the description:
        if desc:
            self.valsDesc[name] = desc
        # setting the variable:
        if name not in self.vals:
            self.vals[name] = value
    
    def removeVariable(self, name):
        self.vals.pop(name)
        self.valsDesc.pop(name)

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

    def interpretString(self, strin):
        slist = strin.splitlines()
        for line in slist :
            self.interpretLine(line)
        
    # ----------------------- Handlers: ---------------------------------------
        
    context_type = ["normal"]
    current_expr = "" #variable to cummulate expression that will be evaluated

    def addContextType(self, t, overlap_word = ""):
        self.context_type.append(t)
        self.handlers[t].start(self.stack[-1])
        if overlap_word != "":
            self.handlers[t].handle(self.stack[-1], overlap_word, "")

    def removeContextType(self, overlap_word = ""):
        k = self.context_type.pop()
        self.handlers[k].end(self.stack[-1])
        if overlap_word != "":
            self.handlers[self.context_type[-1]].handle(self.stack[-1], overlap_word, "")
        
    # word is a string
    def interpretWord(self, word, whitespace):
        env = self.stack[-1]

        # ------------- eval spec chars ---------------
        reg = re.match(rf"(.*){env.evalMarker}(.*)", word)
        if reg:
            self.handlers[self.context_type[-1]].handle(env, reg.group(1), whitespace)
            reg1 = re.match(rf"{env.evalBeginMarker}(.*)", reg.group(2))
            if not reg1: # single variable eval:
                self.interpretString( str(eval(reg.group(2), safe_globals, self.vals)) )
            else: # eval expression:
                self.addContextType("eval", reg1.group(1))
            return
        
        # In any context other than "normal" or "eval", we can find an AVTSEndToken
        reg = re.match(rf"(.*){env.AVTSEndToken}(.*)", word)
        if reg and self.context_type[-1] != "eval" and self.context_type[-1] != "normal":
            # the "prelapping word" is only handled by the currently active handler:
            self.handlers[ self.context_type[-1] ].handle(env, reg.group(1))
            # all the contexts (until the AVTS) are removed (overlapping word = ""):
            while self.context_type[-1] != "AVTS":
                self.removeContextType("")
            # finally, the AVTS environment is removed, with the overlapping word set:
            self.removeContextType(reg.group(2))
            return

        # Finally; pass the word for handling to the current context:
        self.handlers[self.context_type[-1]].handle(env, word, whitespace)
        
        
    # interprets the current line as AVTS command.
    # if it is not AVTS command, returns False
    def interpretLine(self, line_in) :
        line = line_in.rstrip('\n')
        b = (line == line_in)
        linebeg = True
        if re.match(rf"(.*){self.stack[-1].AVTSEndToken}$", line.strip()) and re.match(rf"^{self.stack[-1].AVTSStartToken}(.*)", line.strip()) :
            line = line.strip()
            b = True
            linebeg = False
        if linebeg: self.stack[-1].beginLine()
        reg = re.match(r"(\s*)(\S+)(.*)", line)
        while reg:
            self.interpretWord(reg.group(2), reg.group(1))
            line = reg.group(3)
            reg = re.match(r"(\s*)(\S+)(.*)", reg.group(3))
        if b:
            self.stack[-1].print(line)
        else:
            self.stack[-1].print(line + "\n")
        
