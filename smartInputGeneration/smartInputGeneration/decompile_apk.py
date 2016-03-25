#!/usr/bin/python
import sys
import os
from cli_utils import run_command

class Decompile_Apk:
    
    APKTOOL = 'apktool'
    APKTOOL_LOC = ''
    APKTOOL_PARAMS = ' d --no-src -f  '
         
    decompile_command = ''
    
    outfile = ''
    inpath = ''
    
    def __init__(self, inpath, outfile):
        
        self.inpath = inpath
        self.APKTOOL_LOC = os.path.join(os.path.dirname(__file__), self.APKTOOL)
        
        if not os.path.exists(outfile):
            os.mkdir(outfile)
        
        self.outfile = os.path.abspath(outfile)
        self.decompile_command = './' + self.APKTOOL_LOC + self.APKTOOL_PARAMS

    
    def decompile(self):
        
        files = os.listdir(self.inpath)
        for apkfile in files:
            absfile = os.path.join(os.path.abspath(self.inpath), apkfile)
            if absfile.endswith('.apk'):
                print run_command((self.decompile_command + absfile + ' -o ' + self.outfile), os.getcwd())
        
        


def usage():
    print 'usage: getresources <input_path> <output_path>'


def main():
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
        return
    
    inpath = str(sys.argv[1])
    print inpath
    
    if not os.path.isdir(inpath):
        print 'Fatal error! Invalid input path: ', inpath
        return
        
    if len(sys.argv) == 3:
        outfile = str(sys.argv[2])
        if not os.path.isdir(outfile):
            print 'Output path not present. Creating ...'
            os.mkdir(outfile)
    else:
        print 'Output path not specified. Using current ...'
        outfile = os.getcwd() 

    print inpath, outfile
    
if __name__ == "__main__":
    main()
    

