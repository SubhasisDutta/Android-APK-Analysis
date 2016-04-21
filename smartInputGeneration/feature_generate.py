#!/usr/bin/python

import os
import math
from dict_generator import Dict_Generate

class Feature_Generator:
    
    MAX_WEIGHT = 2
    INPUT_TYPES_FILE_NAME = 'const_data/input_types'
    INPUT_TYPES_FILE = ''
    
    COMPLEX_INPUT_TYPES_FILE_NAME = 'const_data/complex_input_types'
    COMPLEX_INPUT_TYPES_FILE = ''
    
    sample_threshold = 0
    
    input_file = ''
    output_file = ''
    DICT_FILE_NAME = 'const_data/dictionary'
    DICT_FILE = ''
    #STOP_WORD_FILE='const_data/stopwords'
    
    word_list = []
    #stop_word_list = []
    
    """    
    def __init__(self, input_file, output_file, sample_threshold):
        
        self.INPUT_TYPES_FILE = os.path.join(os.path.dirname(__file__), self.INPUT_TYPES_FILE_NAME)
        self.COMPLEX_INPUT_TYPES_FILE = os.path.join(os.path.dirname(__file__),self.COMPLEX_INPUT_TYPES_FILE_NAME)
        
        if not os.path.exists(self.INPUT_TYPES_FILE):
            raise RuntimeError('Input types file does not exist!')
        
        if not os.path.exists(input_file):
            raise RuntimeError('Input file does not exist!')
        
        self.input_file = input_file
        self.output_file = output_file
        self.sample_threshold = sample_threshold
        
        dict_gen = Dict_Generate()
        self.word_list = dict_gen.generate_dict()
        
        self.__get_input_types__()
    """
    
    csv_data = []
    def __init__(self, output_file, sample_threshold):
       
        self.INPUT_TYPES_FILE = os.path.join(os.path.dirname(__file__), self.INPUT_TYPES_FILE_NAME)
        self.INPUT_TYPES_HEX_FILE = os.path.join(os.path.dirname(__file__), 'const_data/type_variation_hex')
        self.COMPLEX_INPUT_TYPES_FILE = os.path.join(os.path.dirname(__file__),self.COMPLEX_INPUT_TYPES_FILE_NAME)

        print "Feature Generator output_file " +output_file
        #print "Feature Generator sample_threshold " +sample_threshold
        self.output_file = output_file
        self.sample_threshold = sample_threshold
        
        self.__get_input_types__()
        #self.input_types = input_types
        
        self.__get_complex_input_types__()
        #self.complex_input_types = complex_input_types
        
        self.__init_hex_types__()
        
        dict_gen = Dict_Generate()
        self.word_list = dict_gen.retrieve_dict()
        
        
        #self.__process_data__(data)
        #return self.__generate_feature_arff__()
    
    def generate(self, data):
        #self.__read_data_file__()
        self.__process_data__(data)
        return self.__generate_feature_arff__()
        
    input_types = []
    """
    def __init_stop_words_list(self):
        if not os.path.exists(self.STOP_WORD_FILE):
            raise RuntimeError('Stop words file does not exist')
        
        file_obj = open(self.STOP_WORD_FILE, 'r')
        for line in file_obj.readlines():
            line = line.strip()
            if line.startswith('#') or len(line) == 0: 
                continue
            
            self.stop_word_list.append(line.strip())
    """
    def __init_dict__(self):
        if not os.path.exists(self.DICT_FILE):
            raise RuntimeError('Dictionary file does not exist')
        
        dict_file_obj = open(self.DICT_FILE, 'r')
        for line in dict_file_obj.readlines():
            line = line.strip()
            #if line not in self.stop_word_list:
            self.word_list.append(line)
        
        #print 'Words:  ', len(self.word_list)
    complex_input_types  = []
    
    def __get_complex_input_types__(self):
        # print 'Reading complex input types file:'
        complex_input_file = open(self.COMPLEX_INPUT_TYPES_FILE, 'r')
        for line in complex_input_file.readlines():
            self.complex_input_types.append(line.strip())
        complex_input_file.close()
        # print ', '.join(self.complex_input_types)
    
    hex_types = []
    def __init_hex_types__(self):
        
        hex_file = open(self.INPUT_TYPES_HEX_FILE, 'r')
        
        for line in hex_file.readlines():
            line = line.strip()
            self.hex_types.append(line)
        
       
    def __get_input_types__(self):
       
        input_types_file = open(os.path.join(os.getcwd(), self.INPUT_TYPES_FILE), 'r')
        for line in input_types_file.readlines():
            if len(line) > 0:
                self.input_types.append(line.strip())
        
        input_types_file.close()
    
    sample_count_simple = {}
    sample_count_complex = {}
    
    def get_input_hex(self, complex_input_type):
        if len(self.input_types) == 0:
            raise RuntimeError('Input types not set!')
        
        if complex_input_type < 1:
            raise ValueError('Invalid input type: ', complex_input_type)
        
        #print 'Input type: ', complex_input_type
        idx = int(math.log(complex_input_type, 2))
        
        if idx < len(self.hex_types):
            return self.hex_types[idx] 
        
            
        
    def get_input_text(self, complex_input_type):
        
        if len(self.input_types) == 0:
            raise RuntimeError('Input types not set!')
        
        if complex_input_type < 1:
            raise ValueError('Invalid input type: ', complex_input_type)
        
        #print 'Input type: ', complex_input_type
        #idx = int(math.log(complex_input_type, 2))
        val = 1
        idx = 0
        while val < complex_input_type:
            val *=2
            idx = idx + 1
                
        if(idx < len(self.input_types)):
            return self.input_types[idx]
        return None
    
    def __count_samples__(self, sample_str):
        
        if len(self.input_types) == 0:
            raise RuntimeError('Input types not set!')
        
        samples = sample_str.split('|')
        val = 0
        found = False
        for sample in samples:
            if sample not in self.input_types:
                continue
            idx = self.input_types.index(sample);
            val += pow(2, idx)
            # Count Simple type
            if not found:
                found = True
                if sample not in self.sample_count_simple.keys():
                    self.sample_count_simple[sample] = 1
                else:
                    self.sample_count_simple[sample] = self.sample_count_simple[sample] + 1
        if str(val) not in self.sample_count_complex.keys():
            self.sample_count_complex[str(val)] = 1;
        else:
            self.sample_count_complex[str(val)] = self.sample_count_complex[str(val)] + 1;
        
        return val
    
    data = []
    
    def __process_data__(self, csv_data):
        
        lineidx =  0
        while lineidx < len(csv_data):
            line = csv_data[lineidx]
            lineidx = lineidx + 1

            data_dict = {}
            data_val = [0] * len(self.word_list)
            entries = line.split(',')
            for entry in entries:
                prop_val = entry.split('=')
                if(len(prop_val) > 1):
                    #data_dict[prop_val[0]] = get_values(prop_val[1])
                    prop_val[1] = prop_val[1].replace('true', '')
                    prop_val[1] = prop_val[1].replace('false', '')
                    if prop_val[0] == '0_inputType':
                        data_dict['input_type_simple'] = prop_val[1]
                        data_dict['input_type_complex'] = self.__count_samples__(prop_val[1])
                    else:
                        if prop_val[0] == '0_id':
                            data_dict[prop_val[0]] = prop_val[1]
                        for word in self.word_list:
                            lower_case_entry = prop_val[1].lower()
                            idx = lower_case_entry.find(word)
                            if idx != -1:
                                word_idx = self.word_list.index(word)
                                weight = 1
                                data_val[word_idx] += weight
            data_dict['data'] = data_val
            self.data.append(data_dict)
                
    def __read_data_file__(self):
        
        # print 'Reading data file ...'
        file_obj = open(self.input_file, 'r')
        self.__process_data__(file_obj.readlines())   
    
    ARFF_RELATION_STR = '@RELATION'
    ARFF_ATTRIBUTE_STR = '@ATTRIBUTE'
    ARFF_DATA_STR = '@DATA'
    
    def __generate_arff_header__(self, arff_data_list, class_list):
        
        arff_data_list.append(self.ARFF_RELATION_STR + ' ' + 'Form_Props-InputType')
        
        for word in self.word_list:
            arff_data_list.append(self.ARFF_ATTRIBUTE_STR + ' ' + word + ' ' + 'NUMERIC')
        
        class_str = ''
        class_str += self.ARFF_ATTRIBUTE_STR + ' ' + '_class_' + ' {' + ','.join(class_list) + '}'
        arff_data_list.append(class_str)
        
        arff_data_list.append(self.ARFF_DATA_STR)
    
    TYPE_SIMPLE = True
    TYPE_COMPLEX = False
           
    def __generate_arff_entry__(self, entry, data_type):
        data_key = entry.keys()
        if 'input_type_simple' not in data_key:
            if self.sample_threshold == 0:
                entry['input_type_simple'] = '?'
                entry['input_type_complex'] = '?'
               
        if sum(entry['data']) == 0 and self.sample_threshold > 0:
            return None
        
        entry_str = ''
        entry_str += ','.join(str(ent) for ent in entry['data'])
        
        input_type_str = entry['input_type_simple']
        if data_type == self.TYPE_SIMPLE:
            input_type_list = input_type_str.split('|')
            for input_type in input_type_list:
                input_type = input_type.strip()
                if len(input_type) == 0:
                    continue;
                
                if input_type not in self.input_types:
                    if self.sample_threshold > 0:
                        #print input_type_str
                        continue
                    
                if self.sample_threshold > 0:
                    if self.sample_count_simple[input_type] < self.sample_threshold:
                        continue
                             
                return entry_str + ',' + input_type
        else:
            input_type = entry['input_type_complex']
            #print input_type
            if self.sample_threshold > 0:
                #Training data
                if self.sample_count_complex[input_type] > self.sample_threshold:
                    return entry_str + ',' + input_type
            else:
                if str(input_type) in self.complex_input_types:
                    return entry_str + ', ' + str(input_type)
                else:
                    return entry_str + ', ?'
        return None
       
    def __generate_feature_arff__(self):
        
        if len(self.data) == 0:
            raise RuntimeError('Data not generated!')
        
        #print 'Generating arff:'
        arff_data_simple = []
        arff_data_complex = []
        
        self.__generate_arff_header__(arff_data_simple, self.input_types)
        self.__generate_arff_header__(arff_data_complex, self.complex_input_types)

        ids = []
        for entry in self.data:
            simple_entry = self.__generate_arff_entry__(entry, self.TYPE_SIMPLE)
            if simple_entry is not None:
                arff_data_simple.append(simple_entry)
            
            complex_entry = self.__generate_arff_entry__(entry, self.TYPE_COMPLEX)
            if complex_entry is not None:
                arff_data_complex.append(complex_entry)
                str_ids = entry['0_id'].split('|')
                ids.append(str_ids[0])
                
        arff_file = open(self.output_file + '_simple.arff', 'w')
        arff_file.write('\n'.join(arff_data_simple))
        arff_file.close()
        
        arff_file = open(self.output_file + '_complex.arff', 'w')
        for line in arff_data_complex:
            arff_file.write(line + '\n')
 
        arff_file.close()
        return ids
        
                