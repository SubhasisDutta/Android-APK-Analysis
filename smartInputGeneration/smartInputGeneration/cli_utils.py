#!/usr/bin/python

import os
import subprocess

"""
    Runs a command in the shell and returns its output
"""
def run_command(commands,  path):
    print commands
    if not path:
        path  = os.getcwd()
    pipe = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
    (output, error) = pipe.communicate()
    if error:
        print error
    return output