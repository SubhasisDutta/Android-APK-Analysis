#!/usr/bin/python
import sys
import os
import codecs

"""
    Removes namespace information from key
"""
def process_key(key):
    act_key = key
    if key.find('}') != -1:
        act_key = key[(key.find('}') + 1):]
    return act_key

"""
    Removes unnecessary data from value string
"""
def process_value(value):
    act_val = value
    if value.find('/') != -1:
        act_val = value[value.find('/')+1:]
    return act_val

"""
    Retrieves id value from element
"""
def get_element_id(element):
    if element is None:
        return None
    for key in element.attrib.keys():
        act_key = process_key(key)
        if act_key == 'id':
            return element.attrib[key]
    return None

"""
    Finds an element from its id by searching all nodes from root
"""
def find_element_by_id(root, element_id):
    for node in root._children:
        id = get_element_id(node)
        if id == element_id:
            return node
    return None

"""
    Returns a dictionary naming every element as key and its parent as value
    Should be used by get_total_map() only
"""
def get_parent_map(root):
    parent_map = {}
    for child in root._children:
        if child in parent_map:
            parent_map[child].append(root)
        else:
            parent_map[child] = (root)
            
    return parent_map 

"""
    Maps every element to its parent
"""
def get_total_map(root):
    
    parent_map = {}
    if len(root._children) == 0:
        return parent_map
    
    parent_map = get_parent_map(root)
    for child in root._children:
        parent_map.update(get_total_map(child))
    
    return parent_map
    
    
def lin_find_child_idx_in_parent(element, parentelement):
    idx = 0;
    for children in parentelement._children:
        if children == element:
            return idx
        idx = idx + 1
    return -1
def lin_find_first_element(lin_element):
    num_children = len(lin_element._children)
    if num_children > 0:
        return lin_element._children[0]
    return None

def lin_find_last_element(lin_element):
    num_children = len(lin_element._children)
    if num_children > 0:
        return lin_element._children[num_children - 1]
    return None
    

def lin_find_neighbors(element, parentelement):
    neighbor_elements = []
    num_children = len(parentelement._children)
    element_idx = lin_find_child_idx_in_parent(element, parentelement)
    
    if element_idx < 0:
        print 'Error'
    elif element_idx == 0:
        if len(parentelement._children) > 1:
            neighbor = parentelement._children[1]
            if neighbor != None:
                if neighbor.tag.find('Layout') == -1:
                    neighbor_elements.append(neighbor)
                else:
                    """Parent is a layout"""
                    while neighbor.tag.find('Layout') != -1:
                        neighbor = lin_find_first_element(neighbor)
                        if neighbor is None:
                            break
                    if neighbor != None:
                        neighbor_elements.append(neighbor) 
                
    elif element_idx > 0:
        if len(parentelement._children) > 1:
            neighbor = parentelement._children[element_idx - 1]
            if neighbor != None:
                if neighbor.tag.find('Layout') == -1:
                    neighbor_elements.append(neighbor)
                else:
                    """Parent is a layout"""
                    while neighbor.tag.find('Layout') != -1:
                        neighbor = lin_find_last_element(neighbor)
                        if neighbor is None:
                            break
                    if neighbor != None:
                        neighbor_elements.append(neighbor)
        if (element_idx + 1) < len(parentelement._children):
            neighbor = parentelement._children[element_idx + 1]
            if neighbor != None:
                if neighbor.tag.find('Layout') == -1:
                    neighbor_elements.append(neighbor)
                else:
                    """Parent is a layout"""
                    while neighbor.tag.find('Layout') != -1:
                        neighbor = lin_find_first_element(neighbor)
                        if neighbor is None:
                            break
                    if neighbor != None:
                        neighbor_elements.append(neighbor)
                    
                    if neighbor.tag.find('Layout') == -1:
                        neighbor_elements.append(neighbor)
        
    return neighbor_elements
    
relative_layout_attrs = [
                         'layout_toLeftOf',
                         'layout_toRightOf',
                         'layout_below',
                         'layout_above',
                         ]

def rel_find_from_neighbors(element, parentelement):
    neighbor_elements = []
    #print 'Hey 2'
    element_id = get_element_id(element)
    for node in parentelement._children:
        if hasattr(node, 'attrib'):
            for key in node.attrib.keys():
                act_key = process_key(key)
                if act_key in relative_layout_attrs:
                    val = process_value(node.attrib[key])
                    if val == element_id:
                        neighbor_elements.append(node)
    return neighbor_elements
    
def rel_find_from_element(element, parentelement):
    neighbor_elements = []
    #print 'Hey'
    for key, value in element.attrib.iteritems():
        act_key = process_key(key)
        if act_key in relative_layout_attrs:
            val = process_value(value)
            neighbor_elements.append(find_element_by_id(parentelement, val))
    return neighbor_elements        
                

def find_nearby_elements(parentelement, element):
    
    elements = []
    if parentelement.tag == 'RelativeLayout':
        elements += rel_find_from_element(element, parentelement)
        if len(elements) == 0:
            elements += rel_find_from_neighbors(element, parentelement)
        if len(elements) == 0:
            elements +=  lin_find_neighbors(element, parentelement)
    elif parentelement.tag == 'LinearLayout' or hasattr(parentelement, '_children'):
        elements += lin_find_neighbors(element, parentelement)
    
    return elements

def find_neighbors(root, element):
    elements = []
    parent_map = get_total_map(root)
    if element in parent_map.keys():
        parentelement = parent_map[element]
        if parentelement is not None:
            elements += find_nearby_elements(parentelement, element)
            #if elements != None:
            #    print 'Neighbors found:', len(elements)
            if len(elements) > 0:
                return [elements[0]]
            return elements
    else:
        print 'Error!!'
        return elements
