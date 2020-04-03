from AVTS import *
from AVTS_helptext import *
import AVTS_text_environment as textenv

sys.argv.pop(0)  # the filename
if (len(sys.argv) == 0 ) :
    print('Not enough arguments')
    exit(-1)

environment = textenv.TextEnvironment()
avts = AVTS(environment, textenv.defaultSkin())

# handles switches in the input line
save_master = False
masterfile = None

while (sys.argv[0])[0] == '-' :
    opt = sys.argv.pop(0)
    if (opt == '-help') :
        print(helptext)
        exit(0)
    if opt == '-save_master' :
        save_master = True
        continue
    m = re.match(r"-f", opt)
    if m :  # found a master file
        masterfile = sys.argv.pop(0)
        print("masterfile = ", masterfile, file = sys.stderr)
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
                avts.setVariableFromExpression( m.group(2), m.group(1), m.group(5) )
            else :
                avts.vals[m.group(2)] = m.group(5)
        continue
    m = re.match(r"-D", opt)
    if m :  # found a variable to be defined
        opt = sys.argv.pop(0)
        m = re.match(r"((\w+)=([a-zA-Z0-9\" ]+))", opt)
        #print(opt, m.groups(), file = sys.stderr)
        if m.group(2) not in avts.vals :
            avts.setVariableFromExpression(m.group(2), m.group(1),
                                           "command line defined variable")
        continue
    print("Bad switch : ", opt, file = sys.stderr)
    exit(-1)

# end of switches: input file must come
inputfile = sys.argv.pop(0)
success = avts.interpret(inputfile)
if not success:
    exit(-1)

# save master file if necessary
if save_master :
    if masterfile is None :
        m = re.match(r"(.*)\.[^.]+", inputfile)
        if m : masterfile = m.group(1) + "_master"
        else : masterfile = inputfile + "_master"
    f = open(masterfile, 'w')
    print("# AVTS master, automatic save", file = f)
    for i in avts.vals :
        print(i +"="+ str(eval(i)) +' "' + avts.vals[i] +'"', file = f)
    f.close()
