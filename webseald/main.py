#!/usr/bin/env python
"""
Usage:  main.py
        main.py [--websealdfile=JUNCTIONDIR --out-dir=TARGETDIR --skipInstanceHeader --debug]

Options:
  --debug   Print debug information
  --websealdfile=FILE   Webseald.conf file for the instance
  --out-dir=DIRECTORY   Directory to store the resulting yaml and conf files in (default: temp or tmp)  Eg. to store in current directoy : --out-dir=.
  --skipInstanceHeader  Do not add the instance configuration to the yaml file (default: will be added)
  -h --help     Show this screen.

"""
from lib import f_processwebsealdconf as f_processwebsealdconf
from docopt import docopt
import tkinter
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw()

def main():
    websealdfile = ''
    args = docopt(__doc__)
    #print(args)
    skipInstanceHeader = False
    debug=False
    outdir=None
    if args['--debug']:
        debug=True
    if args['--skipInstanceHeader']:
        skipInstanceHeader=True
    if args['--websealdfile']:
        #ok
        websealdfile = args['--websealdfile']
    if args['--out-dir']:
        outdir = args['--out-dir']
    if websealdfile == '':
        websealdfile = filedialog.askopenfilename()
    if websealdfile is not None and len(websealdfile) > 0:
        print("\n\nOpening file " + websealdfile)
        f_processwebsealdconf(websealdfile, outdir=outdir, skipInstanceHeader=skipInstanceHeader, debug=debug)

if __name__=='__main__':
   main()
