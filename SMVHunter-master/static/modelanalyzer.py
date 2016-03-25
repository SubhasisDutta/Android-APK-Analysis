#    Copyright (C) 2013  David Sounthiraraj
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import re
import sys
import os

models = []

def parse_method(method):
    """
    parses the given method returns number of locals
    the code block and method name
    """
    #replace the context in every line
    #replace v[0-9] by v, p[0-9] by p, cond[0-9] by cond and goto[0-9] by goto
    #this will give us context free variables and help us to find out the
    #models even if they are embeded in other piece of code
    method = re.sub("v[0-9]", "v", method)
    method = re.sub("p[0-9]", "p", method)
    method = re.sub("cond_[0-9]", "cond", method)
    method = re.sub("goto_[0-9]", "goto", method)


    #extract the code portion
    #replace the annotation portion if present
    ann = re.findall(r"\.annotation.*?\.end annotation", method, re.S)
    if len(ann) > 0:
        method = method.replace(ann[0], "")

    #split each line
    #ignore everything that starts with a '.'
    #create an array with the code block
    code_block = []
    method_name = ""
    for i, line in enumerate(method.split("\n")):
        line = line.strip()
        if i == 0:
            method_name = line
            continue
        if line and not line.startswith("."):
            code_block.append(line)

    return (method_name, code_block)

# check if strings in models appear in code block. If so, vulnerable. Else not vulnerable.
def check_model(code_block, file_name):
    vuln = False
    if len(code_block) == 1:
        if code_block[0] == "return-void":
            print "vulnerable by model noop %s" % file_name
            vuln = True
    else: #others
        code = "".join(code_block)
        for i, model in enumerate(models):
            if model in code:
                print "vulnerable by model %i %s"  % (i, file_name)
                vuln = True
                break
    return vuln

#input : path from mfg_generator.py
def analyze_file(file_name):
    #initialize all vulnerable model in models
    
    populate_model()

    #read all the contents
    f_content = open(file_name).read()

    #now get all the methods in the smali file
    methods = re.findall(r"\.method.*?\.end method", f_content, re.S)
    for i, method in enumerate(methods):
        method_name, code_block = parse_method(method)
        if "checkServerTrusted" in method_name and check_model(code_block, file_name):
            return True
    return False

def populate_model():
    #read the vulnerable models
    for model in open("./r.txt").read().split("="*30):
        models.append(model.strip().replace("\n", ""))
	

