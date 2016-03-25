#!/usr/bin/env python

import sys
import os

from cli_utils import run_command

if len(sys.argv) != 3:
    print 'usage: move_relevant_files.py <source_path> <destination_path>'
    exit()

src_dir = sys.argv[1]
dst_dir = sys.argv[2]
    
if not os.path.exists('relevant_files.db'):
    print 'Relevant files db does not exist!'
    exit()

relevant_file_obj = open('relevant_files.db', 'r')

relevant_files = []

for line in relevant_file_obj.readlines():
    line = line.strip()
    if line not in relevant_files:
        relevant_files.append(line)

for entry in relevant_files:
    file_name = entry
    file_dir = entry[:-4]
    
    file_copy_command = 'cp ' + os.path.join(src_dir, file_name) + ' ' + dst_dir
    dir_copy_command = 'cp -r ' + os.path.join(src_dir, file_dir) + ' ' + dst_dir
    
    run_command(file_copy_command, None)
    run_command(dir_copy_command, None)