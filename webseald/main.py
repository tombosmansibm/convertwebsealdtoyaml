#!/usr/bin/env python
"""
Usage:  main.py
        main.py [--websealdfile=JUNCTIONDIR]

Options:
  --websealdfile=FILE   Webseald.conf file for the instance
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
    if args['--websealdfile']:
        #ok
        websealdfile = args['--websealdfile']
        print(websealdfile)
    if websealdfile == '':
        websealdfile = filedialog.askopenfilename()
    if websealdfile is not None and len(websealdfile) > 0:
        print("\n\nOpening file " + websealdfile)
        f_processwebsealdconf(websealdfile)

if __name__=='__main__':
   main()
