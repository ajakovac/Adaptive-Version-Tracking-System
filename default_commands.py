import copy
import re

def beginC(avts, args):
    args = list(map(lambda x : x.strip(), args.split(",")))
    newenv = copy.copy(avts.topEnv())
    # If the first arg is not in the modder list: its a boolean setting the visibility
    if args[0] not in avts.topEnv().modderList:
        try:
            newenv.visible = avts.evaluate(args[0])
            args.pop(0)
        except:
            raise Exception("Invalid AVTS " + avts.topEnv().beginToken + " argument: "
                            + args[0])
    args.reverse()
    for l in args:
        lamb = newenv.modderList.get(l, None)
        if not lamb: 
            raise Exception("Invalid AVTS " + avts.topEnv().beginToken + " argument: "
                            + l)
        lamb(newenv)
    avts.pushEnv(newenv)

def recoverC(avts, args):
    if args != "":
        raise Exception("AVTS " + avts.topEnv().recoverToken + " can not have any " +
                        "parameters (given parameters: '" + args + "').")
    avts.popEnv()

def resetC(avts, args):
    if args != "":
        raise Exception("AVTS " + avts.topEnv().resetToken + " can not have any " +
                        "parameters (given parameters: '" + args + "').")
    while avts.popEnv(): pass

def defC(avts, args):
    args = list(map(lambda x : x.strip(), args.split(";")))
    if len(args) > 2:
        raise Exception("AVTS " + avts.topEnv().defToken + " can not have at most 2 two"
                        + " parameters (given parameters: '" + args + "').")
    reg = re.match(rf"(.*)\s*=\s*(.*)", args[0])
    if not reg:
        raise Exception("AVTS " + avts.topEnv().defToken + " fisrt argument is not a "
                        + "variable assignment (given argument: '" + args[0] + "').")
    avts.setVariable(reg.group(1), avts.evaluate(reg.group(2)))
    if len(args) == 1: return
    avts.setVariableDescription(reg.group(1), args[1].strip('"'))
