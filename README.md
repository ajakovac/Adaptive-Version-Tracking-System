# Adaptive-Version-Tracking-System
Highly tunable filter determining the visibility of parts of the input document/code.

Many of us have encountered with the situation when we want to write a description of a project, and we do not know the level we should aim. For a starter we should phrase it simpler, for an interested expert we should do it comprehensive and professional, for a follower we should go into details. It applies not only for documentation, but also for code development, and even for book writing, and so on. In a public GUI, for example, there is usually a problem that too many details, and too few details are unwelcome, but the level of datails should depend on the user! Another connected issue is that we may want to make bookkeepeing of the tasks connected to the project. At one hand it should not be part of the documentation, on the other hand the tasks refer to certain parts of the project described in the documentation.

The solution should be a system, where all details, and all level formulations are saved, but we can precisely select which one of these details should appear in the actual version and which one do not. At a first sight it may seem simple, but it will be complicated when we want to recognize cross-dependences, want to assign contributors, and a lot of problems that will show up later.

This project starts with the simple application AVTS.py. This code works with two files, an input file and a master file. The input file can be any text file (including documentations, program codes, etc.) containing AVTS switches, which define and tag 
blocks of the input file. The master file determines whether these blocks appear in the output or not.

# Usage:

AVTS.py \<swiches\> inputfile \<master file\>

available switches:

-help : prints this helptext

-save_update : if there are tags in the input file that are missing from the master file, updates the master file accordingly. The new items are as default unvisible.

The input file is compulsory. The default for the master file is the input file core (without extension) followed by "\_AVTMaster".
