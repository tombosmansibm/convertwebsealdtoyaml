#!/usr/bin/env python
"""
Usage:  main.py
        main.py [--websealdfile=JUNCTIONDIR --skipInstanceHeader --debug]

Options:
  --debug   Print debug information
  --websealdfile=FILE   Webseald.conf file for the instance
  --skipInstanceHeader  Do not add the instance configuraiton to the yaml file (default: will be added)
  -h --help     Show this screen.

"""
from lib import f_processwebsealdconf as f_processwebsealdconf
import os
from docopt import docopt
import tkinter
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw()

def main():
    websealdfile = ''
    args = docopt(__doc__)
    print(args)
    skipInstanceHeader = False
    debug=False
    if args['--debug']:
        debug=True
    if args['--skipInstanceHeader']:
        skipInstanceHeader=True
    if args['--websealdfile']:
        #ok
        websealdfile = args['--websealdfile']
        if debug:
            print(websealdfile)
    if websealdfile == '':
        websealdfile = filedialog.askopenfilename()
    if websealdfile is not None and len(websealdfile) > 0:
        if debug:
            print("\n\nOpening file " + websealdfile)
        f_processwebsealdconf(websealdfile, skipInstanceHeader=skipInstanceHeader, debug=debug)

if __name__=='__main__':
   main()
