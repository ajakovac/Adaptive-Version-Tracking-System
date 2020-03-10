# Adaptive-Version-Tracking-System
Highly tunable filter determining the visibility of parts of the input document/code.

## Motivation
Many of us have encountered with the situation when we want to write a description of a project, and we do not know the level we should aim. For a starter we should phrase it simpler, for an interested expert we should do it comprehensive and professional, for a follower we should go into details. It applies not only for documentation, but also for code development, and even for book writing, and so on. In a public GUI, for example, there is usually a problem that too many details, and too few details are unwelcome, but the level of datails should depend on the user! Another connected issue is that we may want to make bookkeepeing of the tasks connected to the project. At one hand it should not be part of the documentation, on the other hand the tasks refer to certain parts of the project described in the documentation.

The solution should be a system, where all details, and all level formulations are saved, but we can precisely select which one of these details should appear in the actual version and which one does not. At a first sight it may seem simple, but it will be complicated when we want to recognize cross-dependences, want to assign contributors, and a lot of problems that will show up later.

## General description
The logics of the filter is that the lines of the input file is printed according to the current environment. The environment depends on the application forum (eg. txt, pdf, html, etc.), and it has a lot of tunable parameters (for example visibility, text style, color, position, action on clicks, etc.). The environment can be changed by different context functions which maps an environment to an environment, and may depend on external user defined variables. The application of the context functions as well as the definition and use of the user defined varaibles can be changed by the AVTS directives.

The AVTS directives are contained by the input file. All directives are introduced by a remark sign (that can be #, % or //), followed by the AVTS keyword, then a command and the arguments in curly brackets.

#### Currently the available directives are:

**AVTS def** *<variable> [= <value>] ["<description>"]*
defines a variable, optionally assign an initial value to it, and give a description. The user defined variables are unmutable, and theirvalue comes from the FIRST occurance. The reason behind this rule is that the variables are first defined in the command line and later in the input file. Predefined variable is "current" which is used as the visibility variable of the current environment.

**AVTS context** *<visibility bool>, <style description>*
modifies the actual context. The visibility bool is a Python expression,which determines the visibility. The current visibility can be achived under the variable "current". The style description, which is a list of context functions, will act on the basic environment one after another, determining the current environment. The old context is pushed into a stack. All the variables occuring in the expressions or style descriptions must be defined earlier.

**AVTS recover**
restores the last environment from the stack

**AVTS reset**
resets the environment stack, and takes the basic environment.

The defined user variables can be set in the command line as well as in a master file. 

#### Usage:
AVTS.py <swiches> inputfile

available switches:
* *-help* : prints this helptext
* *-f masterfile*: reads in the definitions of the variables from the masterfile. In this case the AVTS define directive may be omitted, if these are shown up already in the master file
* *-save_master* : the defined variables are saved in the master file. If no master file is given, we use the core input file name extended by "_AVTSmaster"
* *-D <variable=value>* : define a variable, and set its value

#### Example:
Try the command *python3 AVTS.py -D x=True basetext0.txt*, and compare it with *python3 AVTS.py -D x=False basetext0.txt*. If you apply the *-save_master* switch, then all the defined variables are written out into a file, where it is easier to overview them.
