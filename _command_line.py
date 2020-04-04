import re

def parseArguments(args, vals):
    masterfile = None
    save_master = False
    while (args[0])[0] == '-' :
        opt = args.pop(0)
        if (opt == '-help') :
            print(helptext)
            exit(0)
        if opt == '-save_master' :
            save_master = True
            continue
        m = re.match(r"-f", opt)
        if m :  # found a master file
            masterfile = args.pop(0)
            #print("masterfile = ", masterfile, file = sys.stderr)
            try :
                f = open(masterfile)
                mastertext = f.read().splitlines()
                f.close()
            except IOError as err :
                print("IOError in master file: {0}".format(err))
            # create the option hash file from the master file
            IDpattern = r'\s*((\w+)\s*=\s*([^"]+))(\s+"([^"]*)")?$'
            for line in mastertext :
                if(len(line) == 0) : continue  # empty line
                if (line[0] == '#') : continue  # remark
                m = re.match(IDpattern, line)
                if(not m) :
                    print("Bad format in master file : ", line)
                if m.group(2) not in avts.vals :
                    avts.setVariableFromExpression(m.group(2),m.group(1),m.group(5))
                else :
                    avts.vals[m.group(2)] = m.group(5)
            continue
        m = re.match(r"-D", opt)
        if m :  # found a variable to be defined
            opt = args.pop(0)
            m = re.match(r"(\w+)=([a-zA-Z0-9\"]+)", opt)
            vals[m.group(1)] = m.group(2)
            continue
        sys.stderr.write("Error: Bad switch : " + opt + "\n")
        exit(-1)
    return (args, masterfile, save_master)

