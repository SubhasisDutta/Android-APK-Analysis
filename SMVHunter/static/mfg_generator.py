
#    Copyright (C) 2013  David Sounthiraraj, Subhasis Duta
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
import json
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
SEEDS = [] # point it could be venerable
#this holds all the key value pair from the AndroidManifest.xml
MANIFEST = {}
#result dict
RESULT = {}
#dict to hold the trust manager implementations
TM = []

file_dictionary={}
file_velnerable=set()
seed_arr=[]
nodes_json=[]

class Node:
    def __init__(self, method_defn):
        self.children = []
        self.parents = []
        self.method_defn = method_defn
    def __repr__(self):
        return self.method_defn

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)#,sort_keys=True, indent=4

    def add_child(self, child_id):
        self.children.append(child_id)

    def add_parent(self, parent_id):
        self.parents.append(parent_id)

def find(regex, string):
    return re.search(regex, string).groups(0)[0]

#input : path of smali file
def parse_sfile(path,r_model_location):
    is_ver = False
    f_content = open(path).read()
    class_name = find("\.class(.*)", f_content).split()[-1]
    methods = re.findall(r"\.method.*?\.end method", f_content, re.S)
    #add the class which implements the trustmanager to seed
    trustmanager = re.findall(r"(\.implements Ljavax/net/ssl/X509TrustManager;)", f_content)
    meth_arr = []
    # populate the class dict with the class and method mapping
    for method in methods:
        #get method name and add to METHODS with class name
        #print "method test: ",method
        key = "%s->%s" %(class_name, find("\.method(.*)", method).split()[-1])
        METHODS.add(key)

        #add constructor (init) to the seeds if trustmanager present
        if trustmanager and "init" in key:
            TM.append(key)
            #check if the class is vulnerable if so add it to the seed
            if modelanalyzer.analyze_file(path,r_model_location):
                SEEDS.append(key)
                file_velnerable.add(path)
                is_ver = True
            else:
                print "file not vulnerable %s" % path
        meth_arr.append((key, method))
    CLASS[class_name] = meth_arr
    return is_ver


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

    for k,v in NODES.iteritems():
        #print "Value : ", v.toJson()
        nodes_json.append(v.toJson())
    file_dictionary["method_tree"] = nodes_json

traversed_nodes=[]

def traverse(apk,seed, node, seen):
    #print "node %s %s %s" % (node, node.parents, seen)
    #print node.parents
    #print "Traversing : ",node.toJson()
    traversed_nodes.append(node.toJson())
    childrens=[]

    #this will handle the case where we register callbacks to the jvm like
    #a socketfactory which does not get called directly so we dont have any
    #active nodes pointing to them. so we see where the class is instanciated.
    if not node.parents:
        class_nm = node.method_defn.split("->")[0]
        for meth_nm, method in CLASS[class_nm]:
            if "init" in meth_nm and meth_nm in NODES and meth_nm not in seen:
                #method is never called. Continue traversing from its class' constructor
                #print meth_nm
                seen.add(meth_nm)

                child = {}
                child["name"]=meth_nm.replace("/", ".").replace("-><init>()V","").replace(";","")
                if len(child["name"]) > 20:
                    child["name"]=child["name"][-20:]
                child["full_name"]=meth_nm.replace("/", ".")
                child_children = traverse(apk,seed, NODES[meth_nm], seen)
                if len(child_children) > 0:
                    child["children"] = child_children
                childrens.append(child)
            elif meth_nm in seen:
                # method is a constructor that is never called; report it as an entry point
                child = {}
                child["name"]=meth_nm.replace("/", ".").replace("-><init>()V","").replace(";","")
                if len(child["name"]) > 20:
                    child["name"]=child["name"][-20:]
                child["full_name"]=meth_nm.replace("/", ".")
                find_key_from_xml(apk,destination_file, seed, meth_nm)
                childrens.append(child)
    else:
        for parent in node.parents:
            child={}
            child["name"]=parent.replace("/", ".").replace("-><init>()V","").replace(";","")
            if len(child["name"]) > 20:
                child["name"]=child["name"][-20:]
            child["full_name"]=parent.replace("/", ".")
            p_node = NODES[parent]
            child_children = traverse(apk,seed, p_node, seen)
            if len(child_children)>0:
                child["children"]=child_children
            childrens.append(child)
    return childrens

#Output
#sample format
#Lcom/chase/sig/android/activity/BillPayPayeeAddVerifyActivity$a;-><init>()V
def find_key_from_xml(apk,destination_file, seed, meth_nm):
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
            #print "result== ", apk, seed, meth_nm, v
            insert_data(apk,destination_file, seed, meth_nm, v)


#write data to db_location file
def insert_data(apk,destination_file, seed, meth_nm, v):
    t={}
    t["seed"]=seed
    t["meth_nm"]=meth_nm
    t["v"]=v
    seed_arr.append(t)
    # with open(destination_file+"_temp",'a+') as f:
    #     f.write(seed + ' ' + meth_nm + ' ' + v + '\n')
    #     #f.write(apk + ' ' + seed + ' ' + meth_nm + ' ' + v + '\n')
    #     f.closed


def parse_android_xml(root):
    #parse the Android Manifest xml and get the name
    #of the of the tag and the android:name attribute
    #and store them as key value
    xml = "%s/AndroidManifest.xml" % root
    tree = ET.parse(xml)

    #get package name from root
    root = tree.getroot()
    package = root.attrib["package"]
    #print "package ",package
    file_dictionary["apk_package"]=package

    for child in tree.iter():
        for k,v in child.attrib.iteritems():
        #get value of ony android:name key and construct a list
            if "{http://schemas.android.com/apk/res/android}name" in k:
                #print "Parse_xml ",k, v
                if v.startswith("."):#prepend package name
                    v = "%s%s" % (package, v)
                MANIFEST[v] = child.tag

    file_dictionary["manifest"]=MANIFEST

def process_apk(root,r_model_location):
    is_velnerable = False
    for path, folders, files in os.walk(root):
        for file in files:
            if file.endswith(".smali") and not re.match("R\$.*", file):
                f_path = os.path.join(path, file)
                #now create the dict
                #print "Parsing file: ",f_path
                flag=parse_sfile(f_path,r_model_location)
                if flag:
                    is_velnerable = True
    file_dictionary["is_velnerable"]=is_velnerable
    #build MCG tree
    parse_methods()



if __name__ == '__main__':
    #root as the decoded path
    root = sys.argv[1] #Location of the APK file
    destination_file = sys.argv[2] #result destination
    r_model_location = sys.argv[3] #location of the model file r.txt
    # print "APK Folder ",root
    # print "Output Destination ",destination_file
    # print "R model",r_model_location
    file_dictionary["apk_location"] = root
    file_dictionary["destination_file"] = destination_file
    file_dictionary["r_model_location"] = r_model_location

    parse_android_xml(root)
    process_apk(root,r_model_location)

    file_dictionary["methods_set"]=list(METHODS)
    print "%d TM and SEED %d apk %s"  % (len(TM), len(SEEDS), root) #TM - trust manager
    file_dictionary["trust_manager"]=TM
    file_seeds=[]
    for s in SEEDS:
        s=s.replace("/", ".")
        file_seeds.append(s)
    file_dictionary["seeds"]=file_seeds
    file_dictionary["files_vernalable"]=list(file_velnerable)

    #yay result.. :p
    seed_nodes=[]
    seed_node_dict={}
    seed_trees=[]
    for seed in SEEDS:
        seed_tree={}
        seed_tree["name"]=seed.replace("/", ".")
        print "seed %s" % seed
        node = NODES[seed]
        #print "seed node: ",node.toJson()
        seed_nodes.append(node.toJson())
        traversed_nodes=[]
        seed_childrens=traverse(root,seed, node, set())
        if len(seed_childrens)>0:
            seed_tree["children"]=seed_childrens
        seed_trees.append(seed_tree)
        seed_node_dict[seed]=traversed_nodes
        #print seed_tree

    file_dictionary["seed_trees"]=seed_trees

    file_dictionary["traverse_nodes"]=seed_node_dict
    file_dictionary["seed_nodes"]=seed_nodes

    file_dictionary["v_end_points"] = seed_arr
    data_str = json.dumps(file_dictionary)
    with open(destination_file,'w') as f:
        f.write(data_str)
        f.closed
    print "Done Static Analysis"





