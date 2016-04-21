#!/usr/bin/python

import os
import codecs
from xml.etree import ElementTree
from layout_processor import process_key, process_value, find_neighbors

class Android_Layout_Parser:
    
    IGNORE_PARAMS = [ 'ems', 'width', 'height', 'padding', 'paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight',
          'textStyle', 'minHeight', 'minWidth', 'clickable', 'focusable', 'nextFocusRight', 'nextFocusLeft', 'nextFocusUp',
          'nextFocusDown', 'textColorHint', 'scrollHorizontally', 'scrollVertically', 'scrollbars', 'gravity', 'selectAllOnFocus',
          'typeface', 'textSize', 'background', 'layout_span', 'textAppearance', 'textColor', 'style', 'cursorVisible', 'drawableRight',
          'drawableLeft', 'visibility', 'scaleType'  'shadowDx', 'shadowDy', 'shadowColor', 'fillViewport' 'adjustViewBounds',
          'focusableInTouchMode', 'fadingEdge', 'ellipsize', 'drawSelectorOnTop', 'divider', 'dividerHeight', 'cropToPadding', 
          'baselineAlignBottom', 'fitsSystemWindows', 'imeOptions', 'orientation',            
          ]

    def __isappdir__(self,path):
    
        if os.path.isfile(path):
            return False
        files = os.listdir(path)
        if 'AndroidManifest.xml' in files:
            return True
        return False
    
    data = []
    res_values_data = {}
    
    def process_app(self, appdir,output_location,file_identifier):
        
        if not os.path.exists(appdir):
            raise RuntimeError('Input path does nor exist: ' + appdir)
        
        app_name = os.path.basename(appdir)
        #self.data.append('#' + app_name)
        
        print 'App: ', app_name
        
        self.res_values_data = {}
        """
        parse every xml in appdir/res/values
        all the children of <resources> will be appended to res_values_data
        """
        for dirpath, dirnames, filenames in os.walk(os.path.join(appdir, 'res/values')):
            for filename in [f for f in filenames if f.endswith(".xml")]:
                self.__parse_xml_values_data__(os.path.join(dirpath, filename))
        
        
        for dirpath, dirnames, filenames in os.walk(os.path.join(appdir, 'res/layout')):
            for filename in [f for f in filenames if f.endswith(".xml")]:
                self.__parse_xml_layout_data__(os.path.join(dirpath, filename))
        file_path = output_location+'/'+file_identifier+'_data.csv'
        file_obj = codecs.open(file_path, encoding='utf-8', mode='w')
        file_obj.write('\n'.join(self.data))
        
        return self.data
    
    def __parse_xml_values_data__(self, xmlfilename):
        """
            Assumption: The file is an absolute file
        """
        print 'Processing xml file: ', xmlfilename
        try:
            xmltree = ElementTree.parse(xmlfilename)
            root = xmltree.getroot()
            if root.tag == 'resources':
                for child in list(root.iter()):
                    if('name' in child.attrib.keys() and child.text is not None):
                        if child.text.startswith('0x'):
                            self.res_values_data[child.attrib['name']] = int(child.text, 16)
                        else:
                            self.res_values_data[child.attrib['name']] = child.text
        except Exception, e:
            print e
     
    def print_attributes_to_string(self, idx, element):
        
        data_str = ''
        k = 0
        keylist = sorted(element.attrib.keys())
        for key in keylist:
            value = element.attrib[key]
            key = process_key(key)
            tagval = process_value(value)
            if tagval in self.res_values_data.keys():
                if  self.res_values_data[tagval] is not None:
                    tagval = tagval + '|' + str(self.res_values_data[tagval])
            if not ((key in self.IGNORE_PARAMS) or (key.startswith('layout'))):
                if k == 0:
                    k = k + 1
                    data_str += str(idx) + '_' + key + '=' + tagval
                else:
                    data_str += ',' + str(idx) + '_' + key + '=' + tagval
        return data_str 
            
    def __parse_xml_layout_data__(self, xmlfilename):
        """
            Assumption: The file is an absolute file
        """
        print 'Processing xml file: ', os.path.basename(xmlfilename)
        try:
            xmltree = ElementTree.parse(xmlfilename)
            root = xmltree.getroot()
            for input_element in root.findall('.//EditText'):
                neighbors = find_neighbors(root, input_element)
                data_str = ''
                # data_str += 'Attr: ' + str(input_element.attrib)
                idx = 0
                data_str += self.print_attributes_to_string(0, input_element)
                idx = 1
                for neighbor in neighbors:
                    data_str += ',' + self.print_attributes_to_string(idx, neighbor)
                    idx = idx + 1
            
                # data_str =
                #outfile.write(data_str)
                
                self.data.append(data_str)
                
            #outfile.close()
        except Exception, err:
            print str(err)