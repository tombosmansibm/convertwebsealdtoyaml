Usage
------
Extract the webseal-config.zip file you obtained by exporting the instance configuration in the LMI.
We need the "webseald-<instancename>.conf" file as input

Alternatively, you can also get a snapshot, this makes more sense if you have a lot of instances to process.

The configuration files can be found under /var/pdweb/<{name of instance}/etc/webseald-{name of instance}.conf

This is tested on Linux and Windows.

It requires Python 3.6+

     
install the prerequisites (in a virtual env)

    docopts
    pyyaml

run headless

    cd <directory>
    python webseald/main.py --websealdfile=<path to webseald-....conf> <--debug> <--skipInstanceHeader>
    
run with prompt
   
    cd <directory>
    python webseald/main.py


select the "webseal.conf" file

There's 2 output file written in your "TEMP" directory (depends on your operating system)
- yaml (a complete instance, or just the "items" (with --skipInstanceHeader))
- conf file (just the changes compared with defaults.conf)

Problems
-------
- 