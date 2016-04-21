#!/usr/bin/env python

import sys
import os
import codecs

from decompile_apk import Decompile_Apk
from layout_parser import Android_Layout_Parser
from feature_generate import Feature_Generator
from cli_utils import run_command

class Predict_Input:
    
    CMD_PREFIX = 'java -cp'
    MODEL_FILE = 'complex.RandomForest.model'
    CLASSIFIER = 'weka.classifiers.trees.RandomForest'
    WEKA = 'tools/weka-3.6.10.jar'
    ARFF_FILE_POSTFIX = '_complex.arff'
    
        
    apk_file = ''
    output_path = None
    feature_gen = None
    
    def __init__(self,output_location,file_identifier):
                
        self.MODEL_FILE = os.path.join(os.path.dirname(__file__),'complex.RandomForest.model')
        self.WEKA = os.path.join(os.path.dirname(__file__),'tools/weka-3.6.10.jar')
        arff_path = output_location+'/'+file_identifier+'_arff_output'
        self.feature_gen = Feature_Generator(arff_path,  0)
            
    weka_output = ''
    ids = []
            
    def predict(self, apk_filename, output_path, output_location, file_identifier):
        
        if not os.path.exists(apk_filename):
            raise RuntimeError('File does not exist!')
        
        self.output_path = os.path.join(os.path.dirname(__file__),output_path)
        self.apk_file = apk_filename
        print 'apk decompile path:', output_path
        
        if self.output_path is None:
            output_path = 'output'
            decompiler = Decompile_Apk(os.path.dirname(os.path.abspath(self.apk_file)), output_path)
            decompiler.decompile()
                
        print 'Parsing xmls ....'
        
        parser = Android_Layout_Parser()
        data = parser.process_app(self.output_path,output_location,file_identifier)
                
        print 'Entries found: ', len(data)
        if len(data) == 0:
            print 'No data!'
            return
        
        os.chdir(os.path.dirname(__file__))
        self.ids = self.feature_gen.generate(data)
        #print ','.join(self.ids)
        
        print 'Running weka ... '
        
        self.weka_output = self.__run_weka__(output_location, file_identifier)
        print self.weka_output
        weka_output = open(self.output_path + '_weka_output' , 'w')
        weka_output.write(self.weka_output)
        weka_output.close() 
        return self.parse_output()
    
    output_types = []
    def parse_output(self):
        
        lines = self.weka_output.split('\n')
        lineidx = 0
        output_type_text = []
        for line in lines:
            
            line = line.strip()
            if (len(line) == 0) or (line.startswith('=') ) or line.startswith('inst#'):
                continue
            
            entries = line.split(' ')
            idx = 0
            for entry in entries :
                if entry:
                    if idx == 2:
                        vals = entry.split(':')
                        value = int(vals[1])
                        output_type = self.feature_gen.get_input_hex(value)
                        self.output_types.append(output_type)
                        output_type_txt = self.feature_gen.get_input_text(value)
                        output_type_text.append(output_type_txt)
                        
                    idx = idx + 1
            lineidx = lineidx + 1
            
        output_dict = {}
        output_dict_txt = {}
        idx = 0
        while idx < len(self.output_types):
            output_dict[self.ids[idx]] = self.output_types[idx]
            output_dict_txt[self.ids[idx]] = output_type_text[idx]
            idx = idx + 1
            
        for key, value in output_dict_txt.iteritems():
            print key, value
        for key, value in output_dict.iteritems():
            print key, value
        
        return output_dict     
                    
    def __run_weka__(self,output_location, file_identifier):
        #arff_output_file = os.path.join(os.path.dirname(__file__), ('arff_output' + self.ARFF_FILE_POSTFIX))
        os.chdir(os.path.dirname(__file__))
        #print 'CWD: ', os.getcwd()
        # file_path = output_location+'/'+file_identifier
        arff_output_file = output_location+'/'+file_identifier+'_arff_output' + self.ARFF_FILE_POSTFIX
        print "Reference loc "+ arff_output_file
        #arff_output_file = 'arff_output' + self.ARFF_FILE_POSTFIX
        cmd_str =   self.CMD_PREFIX  + '  ' \
                        + os.path.join(os.getcwd(),  self.WEKA) + ' ' \
                        + self.CLASSIFIER + ' ' \
                        + '-T ' + arff_output_file + ' ' \
                        + ' -l ' + self.MODEL_FILE \
                        + ' -p 0' 
                        
        return run_command(cmd_str, os.getcwd())

def usage():
    print 'usage: generate_train_model apk_filename'


def main():
    
    if len(sys.argv) != 2:
        usage()
        return
    print sys.argv[1]
    predictor = Predict_Input(sys.argv[1])
    predictor.predict()
    return

if __name__ == '__main__':
    main() 
    