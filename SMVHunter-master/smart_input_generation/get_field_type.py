

#    Copyright (C) 2013  Garrett Greenwood
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


from androguard.core.analysis.analysis import VMAnalysis
from androguard.core.analysis.ganalysis import GVMAnalysis
from androguard.core.bytecodes.apk import APK, AXMLPrinter
from androguard.core.bytecodes.dvm import DalvikVMFormat
from xml.dom import minidom
import argparse
import re
import traceback


class GetFieldType:

    def __init__(self, args):
        self.apk = args.apk
        self.verbosity = args.verbosity

        print "Analyzing " + self.apk

        # analyze the dex file
        self.a = APK(self.apk)

        # get the vm analysis
        self.d = DalvikVMFormat(self.a.get_dex())
        self.dx = VMAnalysis(self.d)
        self.gx = GVMAnalysis(self.dx, None)

        self.d.set_vmanalysis(self.dx)
        self.d.set_gvmanalysis(self.gx)

        # create the cross reference
        self.d.create_xref()
        self.d.create_dref()

        try:
            # get the classes for this apk
            # store them in a dict
            self.classes = self.get_class_dict()

            # Find the R$layout class
            self.Rlayout = self.get_RLayout(self.d.get_classes())

            # Find the R$id class
            self.Rid = self.get_Rid(self.d.get_classes())

            # Store all fields referenced in R$id
            self.fields, self.field_refs = self.get_fields(self.Rid)
        except Exception, e:
            print e



    def get_Rid(self, classes):
        # get R$id class
        for c in classes:
            if("R$id" in c.get_name()):
                # print "Found R$id class at " + c.get_name()
                return c
        raise Exception("R$id not found. apk=" + self.apk)

    def get_RLayout(self, classes):
        # get R$layout class
        layout = []
        for c in classes:
            if("R$layout" in c.get_name()):
                #print "Found R$layout class at " + c.get_name()
                layout.append(c)
        if len(layout) > 0:
            return layout
        raise Exception("R$layout not found. apk=" + self.apk)

    def get_fields(self, Rid):
        # populate fields with field id and name pairs
        # populate field_refs with field id and field reference pairs
        fields = {}
        field_refs = {}
        for f in Rid.get_fields():
            id = hex(f.get_init_value().get_value())
            fields[id] = f.get_name()
            field_refs[id] = f
        return fields, field_refs

    def get_input_fields(self, fields, xml):
        # Return every instance of an EditText field and their inputType in the
        # list of XML's.
        input_fields = {}
        activity = self.get_xml(xml)
        for item in activity.getElementsByTagName("EditText"):
            android_id = None
            input_type = None
            for k, v in item.attributes.itemsNS():
                if k[1] == u'id':
                    android_id = v[1:]
                if k[1] == u'inputType':
                    input_type = v

            #android_id = item.getAttribute("android:id")[1:]
            if android_id:
                id = hex(int(android_id, 16))
                name = fields[id]
                input_fields[id] = input_type

        return input_fields

    def get_xml(self, fil):
        ap = AXMLPrinter(self.a.get_file(fil))
        buff = minidom.parseString(ap.get_buff())

        return buff

    def get_activity_xml(self, activity):
        # Build an list of every layout hex value referenced in activity
        # bytecodes
        hex_codes = []
        for method in activity.get_methods():
            if(method.get_name() == 'onCreate'):
                for idx, instruction in enumerate(method.get_instructions()):
                    # Find setContentView, then parse the passed value from the
                    # previous const or const/high16 instruction
                    if "setContentView" in instruction.show_buff(0):
                        instruction = method.get_code().get_bc().get_instruction(idx-1)
                        if "const" in instruction.get_name():
                            hex_codes.append(self.parse_const(instruction))
                        elif "move" in instruction.get_name():
                            hex_codes.append(self.parse_move(
                                method.get_code().get_bc(), idx - 1))
        if hex_codes == []:
            return False

        # Cross check the list of hex codes with R$layout to retrieve XML
        # layout file name
        for layout in self.Rlayout:
            for field in layout.get_fields():
                if(hex(field.get_init_value().get_value()) in hex_codes):
                    return 'res/layout/%s.xml' % field.get_name()

        raise Exception("XML not found" + str(hex_codes))

    def print_methods(self, obj):
        print obj
        for method in dir(obj):
            if not method.startswith("_"):
                print method

    def parse_const(self, instruction):
        if instruction.get_name() == "const":
            return hex(instruction.get_literals().pop())
        elif instruction.get_name() == "const/high16":
            return hex(instruction.get_literals().pop()) + "0" * 4
        else:
            raise Exception(
                "Unrecognized instruction: " + instruction.get_name())

    def parse_move(self, bc, idx):
        i = bc.get_instruction(idx)
        try:
            register = i.get_output().split(',')[1].strip()
        except IndexError:
            raise Exception(self.apk)
        for x in range(idx - 1, -1, -1):
            i = bc.get_instruction(x)
            if "const" in i.get_name() and register in i.get_output():
                return self.parse_const(bc.get_instruction(x))

    def get_instruction_from_method(self, method):
        instructions = {}
        code = method.get_code()
        bc = code.get_bc()

        idx = 0
        for i in bc.get_instructions() :
            instructions[idx] = i
            idx += i.get_length()
        return instructions


    def infer_implicit_types(self, class_object, text_fields):
        for text_field in text_fields:
            for path in text_field.tainted_field.get_paths():
                access, field_id = path[0]

                # get the method id
                m_idx = path[1]

                if access == "R":
                    # get the method object from the vm
                    method = self.d.get_method_by_idx(m_idx)
                    # print "offset is %s" % field_id
                    # method.show()
                    code = method.get_code()
                    bc = code.get_bc()

                    idx = 0
                    reg_to_follow = ""

                    bc_iter = iter(bc.get_instructions())
                    for i in bc_iter:
                        if field_id == idx:
                            #get the register for the iget-object
                            reg_to_follow = i.get_output().split(',')[0].strip()

                            #go down the iter till we reach a invoke_static
                            #with the same register
                            while(True):
                                try:
                                    i = next(bc_iter)
                                    if i.get_name() == "invoke-static" and reg_to_follow in i.get_output() and "parse" in i.get_output():
                                        #get the type of field
                                        #TODO add more cases
                                        if i.get_output().endswith("F"):
                                            text_field.type = 'float'
                                        elif i.get_output().endswith("I"):
                                            text_field.type = 'integer'
                                        elif i.get_output().endswith("B"):
                                            text_field.type = 'byte'
                                        elif i.get_output().endswith("S"):
                                            text_field.type = 'short'
                                        elif i.get_output().endswith("C"):
                                            text_field.type = 'char'
                                        elif i.get_output().endswith("J"):
                                            text_field.type = 'long'
                                        elif i.get_output().endswith("D"):
                                            text_field.type = 'double'
                                        elif i.get_output().endswith("V"):
                                            text_field.type = 'void'
                                        reg_to_follow = ""
                                        break
                                except StopIteration, e:
                                    break



                        idx += i.get_length()

    def get_class_fields(self, clazz):
        class_fields = {}
        for f in clazz.get_fields():
            class_fields[f.get_name()] = f
        return class_fields

    def get_class_dict(self):
        classes = {}
        for clazz in self.d.get_classes():
            # get the name for using as key
            clazz_name = re.search(
                "L(.*);", clazz.get_name()).group(1).replace("/", ".")
            classes[clazz_name] = clazz

        return classes

    def get_tainted_and_class_field(self, class_object, field, class_fields):
        # print "analyzing field %s" %  field
        for method in class_object.get_methods():
            idx = 0
            register = ""
            inst_iter = iter(method.get_instructions())
            for i in inst_iter:
                if ("const" == i.get_name() or "const/high16" == i.get_name()) and field == self.parse_const(i):
                    # get the register in which the constant is assigned
                    register = i.get_output().split(',')[0].strip()

                    while(True):
                        try:
                            # next instruction
                            i = next(inst_iter)
                        except StopIteration:
                            return

                        # follow the register to the next invoke-virtual of
                        # findViewById
                        if (register in i.get_output() and "findViewById" in i.get_output()) and "invoke-virtual" in i.get_name():
                            # print i.get_name(), i.get_output(), method.get_name()
                            # and get the register of that output
                            register = i.get_output().split(',')[1].strip()

                        if i.get_name() == "move-result-object" and register in i.get_output():
                            register = i.get_output().strip()

                        if i.get_name() == "iput-object":
                            out_sp = re.search(
                                r".*, (.*)->(\b[\w]*\b) (.*)", i.get_output()).groups()

                            # now get the field from the class object
                            tainted_field = self.dx.get_tainted_field(
                                out_sp[0], out_sp[1], out_sp[2])

                            class_field = class_fields[out_sp[1]]

                            return tainted_field, class_field

    def analyze(self):
        # self.print_methods(a)
        num_text_fields = 0
        try:
            for clazz in self.a.get_activities():
                try:
                    print "analyzing activity %s" % clazz
    
                    if clazz in self.classes:
                        class_object = self.classes[clazz]
    
                        # Find all XML layouts referenced in setContentView in activity
                        # bytecodes
                        self.activity_xml = self.get_activity_xml(class_object)
                        if not self.activity_xml:  # if not XML is referenced
                            print "No XML's found in %s" % clazz
                            continue
    
                        # Extract inputTypes from XML
                        self.inputTypes = self.get_input_fields(
                            self.fields, self.activity_xml)
    
                        # get all the fields in the current class
                        class_fields = self.get_class_fields(class_object)
    
                        # Combine all information into a TextField array
                        text_fields = []
                        for f in self.inputTypes:
                            tainted_field = None
                            class_field = None
                            
                            #try to get the instance reference
                            instance_ref = self.get_tainted_and_class_field(class_object, f, class_fields)
                            
                            if  instance_ref:
                                tainted_field, class_field = instance_ref
                            
                                tf = TextField(f, self.fields[f], self.inputTypes[
                                               f], self.field_refs[f], tainted_field, class_field)
                                text_fields.append(tf)
    
                        if text_fields == []:
                            print("No text fields found in %s" % self.activity_xml)
                        else:
                            self.infer_implicit_types(class_object, text_fields)
    
                        # Print all text fields found
			# Write to file
			file = open("smartInput.db","a")
                        for tf in text_fields:
                            print(tf)
			    file.write(clazz+";"+str(tf)+"\n")
                            num_text_fields += 1
			file.close()
                except Exception, e:
                    print e
#                    traceback.print_exc()
    
            if num_text_fields > 0:
                print "%i text fields identified in %s" % (num_text_fields, self.apk)

        except Exception, e:
            print e
            if num_text_fields > 0:
                print "%i text fields identified in %s" % (num_text_fields, self.apk)

class TextField:

    def __init__(self, id, name, type, reference, tainted_field, class_field):
        self.id = id
        self.name = name
        self.type = type
        self.ref = reference
        self.tainted_field = tainted_field
        self.class_field = class_field

    def get_id(self, in_hex=True):
        if(in_hex):
            return hex(self.id)
        else:
            return int(self.id)

    #TODO add more types
    type_lookup = {'': None,
                   u'0x00000002': 'class_number',
                   u'0x00000003': 'phone',
                   u'0x00000004': 'dateTime',
                   u'0x00000081': 'textPassword',
                   u'0x00000021': 'textEmailAddress',
                   }

    def get_type_class(self):
        #try:
        #    return self.type_lookup[self.type]
        #except KeyError:
        #    return self.type
        
        if self.type == None:
            return 'NONE'
        try:
            type_int = int(self.type, 16)
        except Exception:
            return self.type

        if type_int % 16 == 0:
            return 'TYPE_NULL'
        elif type_int % 16 == 1:
            return 'TYPE_CLASS_TEXT'
        elif type_int % 16 == 2:
            return 'TYPE_CLASS_NUMBER'
        elif type_int % 16 == 3:
            return 'TYPE_CLASS_PHONE'
        elif type_int % 16 == 4:
            return 'TYPE_CLASS_DATETIME'
        else:
            return 'TYPE_CLASS_NOT_RECOGNIZED'

    def get_type_variation(self, type_class):
        try:
            type_int = int(self.type, 16)
            var = hex((type_int / 16) % 256)
        except Exception:
            return ''
        
        if type_class == 'TYPE_NULL':
            return 'NONE'
        elif type_class == 'TYPE_CLASS_TEXT':
            if var == '0x0':
                return 'TYPE_TEXT_VARIATION_NORMAL'
            if var == '0x1':
                return 'TYPE_TEXT_VARIATION_URI'
            if var == '0x2':
                return 'TYPE_TEXT_VARIATION_EMAIL_ADDRESS'
            if var == '0x3':
                return 'TYPE_TEXT_VARIATION_EMAIL_SUBJECT'
            if var == '0x4':
                return 'TYPE_TEXT_VARIATION_SHORT_MESSAGE'
            if var == '0x5':
                return 'TYPE_TEXT_VARIATION_LONG_MESSAGE'
            if var == '0x6':
                return 'TYPE_TEXT_VARIATION_PERSON_NAME'
            if var == '0x7':
                return 'TYPE_TEXT_VARIATION_POSTAL_ADDRESS'
            if var == '0x8':
                return 'TYPE_TEXT_VARIATION_PASSWORD'
            if var == '0x9':
                return 'TYPE_TEXT_VARIATION_VISIBLE_PASSWORD'
            if var == '0xa':
                return 'TYPE_TEXT_VARIATION_WEB_EDIT_TEXT'
            if var == '0xb':
                return 'TYPE_TEXT_VARIATION_FILTER'
            if var == '0xc':
                return 'TYPE_TEXT_VARIATION_PHONETIC'
            if var == '0xd':
                return 'TYPE_TEXT_VARIATION_WEB_EMAIL_ADDRESS'
            if var == '0xe':
                return 'TYPE_TEXT_VARIATION_WEB_PASSWORD'

        elif type_class == 'TYPE_CLASS_NUMBER':
            if var == '0x0':
                return 'TYPE_NUMBER_VARIATION_NORMAL'
            if var == '0x1':
                return 'TYPE_NUMBER_VARIATION_PASSWORD'

        elif type_class == 'TYPE_CLASS_DATETIME':
            if var == '0x0':
                return 'TYPE_DATETIME_VARIATION_NORMAL'
            if var == '0x1':
                return 'TYPE_DATETIME_VARIATION_DATE'
            if var == '0x2':
                return 'TYPE_DATETIME_VARIATION_TIME'

        return ''

    def get_type_flags(self, type_class):
        return []

    def __str__(self):
        type_class = self.get_type_class()
        type_var = self.get_type_variation(type_class)
        type_flags = ', '.join(self.get_type_flags(type_class))
        return 'name: %s;id: %s;type: %s;variations: %s;flags: %s;' % (
            self.name, self.id, type_class, type_var, type_flags)


def start():
    parser = argparse.ArgumentParser(description='TODO')

    parser.add_argument('apk', help='The location of the .apk file to analyze')
    parser.set_defaults(func=GetFieldType.analyze)

    parser.add_argument("-v", "--verbosity", action="count",
                        default=0, help="increase output verbosity")

    args = parser.parse_args()
    gft = GetFieldType(args)

    args.func(gft)

if __name__ == '__main__':
    start()
