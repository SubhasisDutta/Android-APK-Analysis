
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


import os
import re
import sys
import modelanalyzer
import xml.etree.ElementTree as ET

#increase recursion limit
sys.setrecursionlimit(40000)

#contains all the methods that are local, i.e which are
#present in the smali code. jvm methods are not included
METHODS = set()
#all the classes in the apk with
CLASS = {}
#contains all the nodes
NODES = {}
#this has all the class names that implement x509trustmanager
SEEDS = []
#this holds all the key value pair from the AndroidManifest.xml
MANIFEST = {}
#result dict
RESULT = {}
#dict to hold the trust manager implementations
TM = []
class Node:
    def __init__(self, method_defn):
        self.children = []
        self.parents = []
        self.method_defn = method_defn
    def __repr__(self):
        return self.method_defn

    def add_child(self, child_id):
        self.children.append(child_id)

    def add_parent(self, parent_id):
        self.parents.append(parent_id)

def find(regex, string):
    return re.search(regex, string).groups(0)[0]

#input : path of smali file
def parse_sfile(path):
    f_content = open(path).read()
    class_name = find("\.class(.*)", f_content).split()[-1]
    methods = re.findall(r"\.method.*?\.end method", f_content, re.S)
    #add the class which implements the trustmanager to seed
    trustmanager = re.findall(r"(\.implements Ljavax/net/ssl/X509TrustManager;)", f_content)
    meth_arr = []
    # populate the class dict with the class and method mapping
    for method in methods:
	#get method name and add to METHODS with class name
        key = "%s->%s" %(class_name, find("\.method(.*)", method).split()[-1])
        METHODS.add(key)
	
        #add constructor (init) to the seeds if trustmanager present
        if trustmanager and "init" in key:
            TM.append(key)
            #check if the class is vulnerable if so add it to the seed
            if modelanalyzer.analyze_file(path):
                SEEDS.append(key)
            else:
                print "file not vulnerable %s" % path

        meth_arr.append((key, method))

    CLASS[class_name] = meth_arr


def parse_methods():
    for cls, methods in CLASS.iteritems():
        for meth_name, method in methods:
            #create a node for the current method
            if meth_name in NODES:
                node = NODES[meth_name]
            else:
                node = Node(meth_name)

            #for each method invocation in the current method
            #check if the node for the method invocation is present
            #if so add the current meth as parent else create one
            #and add it. add each invocation as a child to the
            #current node
            for inv in re.findall(r"invoke-.*", method):
                t_inv = inv.split()[-1]
                if t_inv in METHODS:
                    #updating parents
                    if t_inv in NODES:
                        c_node = NODES[t_inv]
                    else:
                        c_node = Node(t_inv)
                    c_node.add_parent(meth_name)
                    NODES[t_inv] = c_node

                    #now add the node as a child to the current method
                    node.add_child(t_inv)
            NODES[meth_name] = node

def traverse(apk, seed, node, seen):
    #print "node %s %s %s" % (node, node.parents, seen)

    #this will handle the case where we register callbacks to the jvm like
    #a socketfactory which does not get called directly so we dont have any
    #active nodes pointing to them. so we see where the class is instanciated.
    if not node.parents:
        class_nm = node.method_defn.split("->")[0]
        for meth_nm, method in CLASS[class_nm]:
	    
            if "init" in meth_nm and meth_nm in NODES and meth_nm not in seen:
		#method is never called. Continue traversing from its class' constructor
                seen.add(meth_nm)
                traverse(apk, seed, NODES[meth_nm], seen)
            elif meth_nm in seen:
		# method is a constructor that is never called; report it as an entry point
                find_key_from_xml(apk, seed, meth_nm)
    else:
        for parent in node.parents:
            p_node = NODES[parent]
            traverse(apk, seed, p_node, seen)

#Output
#sample format
#Lcom/chase/sig/android/activity/BillPayPayeeAddVerifyActivity$a;-><init>()V
def find_key_from_xml(apk, seed, meth_nm):
    #format the meth name to make fully qualified name
    #replace the L in the start
    meth_nm = re.sub("^L", "", meth_nm)
    if "$" in meth_nm:
        meth_nm = meth_nm.split("$")[0]
    else:
        meth_nm = meth_nm.split(";")[0]

    meth_nm = meth_nm.replace("/", ".")
    for k,v in MANIFEST.iteritems():
        if meth_nm in k and meth_nm not in RESULT:
            RESULT[meth_nm] = v
            print "result== ", apk, seed, meth_nm, v
            insert_data(apk, seed, meth_nm, v)


#write data to db_location file
def insert_data(apk, seed, meth_nm, v):
    with open('output.db','a') as f:
	f.write(apk + ' ' + seed + ' ' + meth_nm + ' ' + v + '\n')
    f.closed


def parse_android_xml(root):
    #parse the Android Manifest xml and get the name
    #of the of the tag and the android:name attribute
    #and store them as key value
    xml = "%s/AndroidManifest.xml" % root
    tree = ET.parse(xml)

    #get package name from root
    root = tree.getroot()
    package = root.attrib["package"]

    for child in tree.iter():
        for k,v in child.attrib.iteritems():
	    #get value of ony android:name key and construct a list
            if "{http://schemas.android.com/apk/res/android}name" in k:
		#print k, v
                if v.startswith("."):#prepend package name
                    v = "%s%s" % (package, v)
                MANIFEST[v] = child.tag
	    	
def process_apk(root):
    for path, folders, files in os.walk(root):
        for file in files:
            if file.endswith(".smali") and not re.match("R\$.*", file):
                f_path = os.path.join(path, file)
                #now create the dict
                parse_sfile(f_path)
    
    #build MCG tree
    parse_methods()



if __name__ == '__main__':
    #root as the decoded path
    root = sys.argv[1]
    
    parse_android_xml(root)
    process_apk(root)

    print
    print "%d TM and SEED %d apk %s"  % (len(TM), len(SEEDS), root)
    print

    #yay result.. :p
    for seed in SEEDS:
        print "seed %s" % seed
        node = NODES[seed]
        print node, root
        traverse(root, seed, node, set())





