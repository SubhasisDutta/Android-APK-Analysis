#!/usr/bin/env python

import sys
import os

from cli_utils import run_command

def main():
    
    if len(sys.argv) != 2:
        return
    print sys.argv[1]
    
    input_path = sys.argv[1]
    dirlist = os.listdir(sys.argv[1])
    
    rel_file_obj = open('relevant_files.db', 'r')
    rel_files = []
    
    for line in rel_file_obj.readlines():
        line = line.strip()
        rel_files.append(line)
    
    print 'Relevant files:' , len(rel_files)
    #print '\n'.join(rel_files)
    
    for filename in dirlist:
        if os.path.isdir(filename):
            continue
        
        abs_file = os.path.join(input_path, filename)
        if abs_file in rel_files:
            cmd = "python get_field_type.py '" + abs_file + "'"
            print run_command(cmd, None)
        
    
if __name__ == '__main__':
    main() 
