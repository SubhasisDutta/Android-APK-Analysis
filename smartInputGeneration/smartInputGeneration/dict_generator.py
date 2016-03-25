#!/usr/bin/python
import os

#from nltk.stem.porter import PorterStemmer

from re import finditer
from re import compile        
    

class Dict_Generate:
    
    DEBUG = True
    
    STOP_WORDS_FILE_NAME = 'const_data/stopwords'
    STOP_WORDS_FILE = ''
    
    DICT_FILE_NAME = 'const_data/dictionary'
    DICT_FILE = ''
    
    TEXT_FIELDS = ['text', 'hint']
    TXT_SEPARATORS = [' ', '_', '/', '-']
    
    porter_stemmer = None
        
    stop_words_list = []
    txt_list = []    
    dictionary = []
        
    def __init__(self):
        #if not os.path.exists(data_file):
        #    raise RuntimeError('Input file not fouind: ' + data_file)
        #self.input_file = data_file
        #self.porter_stemmer = PorterStemmer()
        self.DICT_FILE = os.path.join(os.path.dirname(__file__), self.DICT_FILE_NAME)
    
    def generate_dict(self):
        self.__init_stop_words__()
        self.__extract_text__()
        self.___extract_key_words___()
        return self.dictionary
    
    def retrieve_dict(self):
        #self.__init_stop_words__()
        self.__init_word_list__()
        return self.dictionary
    
    
    def __init_stop_words__(self):
        
        if self.DEBUG:
            print 'Generating stop words list'
        
        if self.porter_stemmer is None:
            raise RuntimeError('Stemmer not initialized!')
        
        file_obj = open(self.STOP_WORDS_FILE, 'r')
        for line in file_obj.readlines():
            if line.startswith('#'):
                continue
            if len(line) > 0 :
                line = line.strip()
                stemmed = self.porter_stemmer.stem(line)
                if len(stemmed) > 0:
                    self.stop_words_list.append(stemmed)
                    
        if self.DEBUG:
            print "Stop Words:"
            print '\t'.join(self.stop_words_list)
    
    def __init_word_list__(self):
        if not os.path.exists(self.DICT_FILE):
            raise RuntimeError('Dictionary file does not exist')
                       
        dict_file_obj = open(self.DICT_FILE, 'r')
        for line in dict_file_obj.readlines():
            if line.startswith('#'):
                continue
            if line[0].isupper():
                continue
            if len(line) > 0:
                try:
                    line = line.replace("'", "")
                    word = line.strip()
                    if word not in self.dictionary:
                        self.dictionary.append(word)
                except Exception, e:
                    print 'Error processing word:' , line
            
        #print 'Words:  ', len(self.dictionary)
        
        
    def __extract_text__(self):
        
        if self.DEBUG:
            print 'Extracting text ...'
        
        if len(self.input_file) == 0:
            raise RuntimeError('Input file not present!')
        
        file_obj = open(self.input_file)
        
        num_vals = 0
        for line in file_obj.readlines():
            if line.startswith('#'):
                continue
            entries = line.split(',')
            for entry in entries:
                prop_val = entry.split('=')
                if len(prop_val) > 1:
                    for param in self.TEXT_FIELDS:
                        if prop_val[0].find(param) != -1:
                            if prop_val[1].find('|') != -1:
                                vals = prop_val[1].split('|')
                                for val in vals:
                                    if len(val) > 0:
                                        self.txt_list.append(val)
                                        num_vals = num_vals + 1
                            else:
                                if len(val) > 0:
                                    self.txt_list.append(val)
                                    num_vals = num_vals + 1
        
        file_obj.close()
        
        if self.DEBUG:
            print 'Words found: ', num_vals
    
    
    def __add_item_to_dict__(self,item):
    
        pattern = compile('[^a-z]')
        item = item.lower()
        item = pattern.sub('', item)
        if (item not in self.dictionary and item not in self.stop_words_list):
            if len(item) > 2:
                self.dictionary.append(item)
                
    def __camel_case_split__(self, identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]
    
    def ___extract_key_words___(self):
        
        if self.DEBUG:
            print 'Extracting keywords ...'
        
        #if len(self.stop_words_list) == 0:
         #   raise RuntimeError('Stop words missing!')
        
        if len(self.txt_list) == 0:
            raise RuntimeError('Text entries missing!')
        
        for line in self.txt_list:
            line = line.strip()
            if len(line) == 0:
                continue
            camelcase_split = self.__camel_case_split__(line)
            for item in camelcase_split:
                found = False
                for separator in self.TXT_SEPARATORS:
                    if item.find(separator) != -1:
                        found = True
                    vals = item.split(separator)
                    for val in vals:
                        self.__add_item_to_dict__(val)
                if not found:
                    self.__add_item_to_dict__(item)

        
        
        
