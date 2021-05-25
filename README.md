Usage
------
Extract the webseal-config.zip file you obtained by exporting the instance configuration.
We need the "webseald-<instancename>.conf" file as input


This is tested on Linux and Windows.

It requires Python 3.6+

     
install the prerequisites (in a virtual env)

run headless

    cd <directory>
    webseald/main.py --websealdfile=<path to webseald-....conf>
    

run with prompt
   
    cd <directory>
    webseald/main.py


select the "webseal.conf" file

There's 2 output file written in your "TEMP" directory (depends on your operating system)
- yaml 
- conf file (just the changes)

Problems
-------
- multiple entries are not imported due to a limitation in the configparser library
-