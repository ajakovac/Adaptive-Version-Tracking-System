helptext = u"""
\033[1mAdaptive Version Tracking System (AVTS)\033[m:
this system is a filter with higly tunable filtering rules.

\033[1mGeneral description\033[m
The logics of the filter is that the lines of the input file is printed according to the current environment. The environment depends on the application forum (eg. txt, pdf, html, etc.), and it has a lot of tunable parameters (for example visibility, text style, color, position, action on clicks, etc.). The environment can be changed by different context functions which maps an environment to an environment, and may depend on external user defined variables. The application of the context functions as well as the definition and use of the user defined varaibles can be changed by the AVTS directives.

The AVTS directives are contained by the input file. All directives are introduced by a remark sign (that can be #, % or //), followed by the AVTS keyword, then a command and the arguments.

\033[1mCurrently the available directives are\033[m:

\033[3m# AVTS def <variable> [= <value>] ["<description>"]\033[m: 
defines a variable, optionally assign an initial value to it, and give a description. The user defined variables are unmutable, and theirvalue comes from the FIRST occurance. The reason behind this rule is that the variables are first defined in the command line and later in the input file. Predefined variable is "current" which is used as the visibility variable of the current environment.

\033[3m# AVTS context <visibility bool>, <style description>\033[m: 
modifies the actual context. The visibility bool is a Python expression,which determines the visibility. The current visibility can be achived under the variable "current". The style description, which is a list of context functions, will act on the basic environment one after another, determining the current environment. The old context is pushed into a stack. All the variables occuring in the expressions or style descriptions must be defined earlier.

\033[3m# AVTS recover\033[m: 
restores the last environment from the stack

\033[3m# AVTS reset\033[m: 
resets the environment stack, and takes the basic environment.
The defined user variables can be set in the command line as well as in a master file.

\033[3m# AVTS replace\033[m: 
replaces the variable with its value transformed to string.
The defined user variables can be set in the command line as well as in a master file.

\033[1mUsage\033[m:
\033[3mAVTS.py <swiches> inputfile\033[m,

where the available switches are

\033[3m-help\033[m: prints this helptext
\033[3m-f masterfile\033[m: reads in the definitions of the variables from the masterfile. In this case the AVTS define directive may be omitted, if these are shown up already in the master file
\033[3m-save_master\033[m: the defined variables are saved in the master file. If no master file is given, we use the core input file name extended by "_AVTSmaster"
\033[3m-D <variable=value>\033[m: define a variable, and set its value

\033[1mExample\033[m:
Try the command python3 AVTS.py -D x=True basetext0.txt, and compare it with python3 AVTS.py -D x=False basetext0.txt. If you apply the -save_master switch, then all the defined variables are written out into a file, where it is easier to overview them.
"""
