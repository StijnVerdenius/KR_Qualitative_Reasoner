# Qualitative Reasoning
### QR-solver for course Knowledge Representation

----

#### Summary:

This repository contains an implementation of a QR solver. 
You can run it with or without trace

#### Calling The Solver:

Arguments:

- **[inputfile]**, which has to be in json format, defaults to "sink_problem"
- **[do_trace] = 'True' or 'False'**, which is a boolean wether you want to do a trace for the start and target states specified in their respective jsonfile in the data folder, defaults to False

Note: If you specify [do_trace], then [inputfile] has to be specified too. Reversed is okay however.

Please call the solver using one of the following commands:

###### Linux/Mac-os:

    ./QR [inputfile] [do_trace]
    
*or*

    source QR.sh [inputfile] [do_trace]
    
*or* 

    sh QR.sh [inputfile] [do_trace]
    
*or* 

    . QR.sh [inputfile] [do_trace]
    
*or* 

    bash QR.sh [inputfile] [do_trace]
    
###### Windows (not tested, so no guarentee to work)

    QR.bat [inputfile] [do_trace]
    
*or install something to call sh files and call:*

    sh QR.sh [inputfile] [do_trace]
    
#### Requirements:

Please make sure you have a working python version (3.5 or higher installed).
For packages, see the requirements.txt file.
If you have multiple python versions on your machine, make sure to activate an environment that can support all of the above, before calling the program



###-
###### extra: sink.hgp contains a garp3 file of the sink problem