Usage
------
Extract the webseal-config.zip file you obtained by exporting the junction configuration.
We need the "junctions" directory.


This is tested on Linux and Windows.

It requires Python 3.6+

     
install the prerequisites (in a virtual env)

run headless

    cd <directory>
    isamjunction/main.py --junctiondir=<directory to junctions>
    

run with prompt
   
    cd <directory>
    isamjunction/main.py


select the "junctions directory"

The output is separate yaml files you can use in plays that are built for https://github.com/IBM-Security/isam-ansible-collection

Specifically:
 https://github.com/IBM-Security/isam-ansible-collection/tree/master/roles/web/configure_reverseproxy_junctions

To do
-------
- so far , the output yaml file is not tested yet (not deployed yet)
- logic for the http/https ports needs to be verified
- most fields are covered, but still some missing (eg. LTPA)