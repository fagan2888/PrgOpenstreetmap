#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import re
import xml.etree.cElementTree as ET
import openstrmap.helper as hlp
import openstrmap.fixaddr as fxad
from time import time

import cerberus

import schema

NODES_PATH = "openstrmap\\nodes.csv"
NODE_TAGS_PATH = "openstrmap\\nodes_tags.csv"
WAYS_PATH = "openstrmap\\ways.csv"
WAY_NODES_PATH = "openstrmap\\ways_nodes.csv"
WAY_TAGS_PATH = "openstrmap\\ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

TAGS_FIELDS = ['id', 'key', 'value', 'type']


def get_field_values(element, fields):
    """ Return a list of values corresponding to specified element fields """
    values = {}
    for field in fields:
        values[field] = element.attrib.get(field)
    return values

def get_node_tag(element, root):
    """ Process tag element and return a dictionary with specified tag attributes. 

    Args:
    element (ET.Element): tag element for processing
    root (ET.Element): top level tag of element
    
    Returns:
    Dictionary with the following keys and values:
        - id: the top level node id attribute value
        - key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is
        - value: the tag "v" attribute value
        - type: either the characters before the colon in the tag "k" value or "regular" if a colon is not present.
    If key contains PROBLEMCHARS returns None

    """
    values = {}
    values["id"] = root.attrib.get("id")
    key = element.attrib.get("k")
    node_key = key
    node_type = "regular"
    m = LOWER_COLON.match(key)
    if m:
        node_type, node_key = key.split(":",1)
    
    if PROBLEMCHARS.search(node_key):
        return None

    values["key"] = node_key
    values["type"] = node_type
    values["value"] = element.attrib.get("v")
    
    return values

def get_way_node(element, root, ind):
    """  Process tag element and return a dictionary with specified attributes
    
    Args:
    element (ET.Element): tag element for processing
    root (ET.Element): the top level element (way)
    ind (int): the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element
    

    Returns:
    Dictionary with the following fields:
        - id: the top level element (way) id
        - node_id: the ref attribute value of the nd tag
        - position: ind
    """
    values = {}
    values["id"] = root.attrib.get("id")
    values["node_id"] = element.attrib.get("ref")
    values["position"] = ind
    return values

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular', fixer=None):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        node_attribs = get_field_values(element, NODE_FIELDS)
    elif element.tag == 'way':
        way_attribs = get_field_values(element, WAY_FIELDS)
        ind = 0
        for tg in element.iter("nd"):
            way_node = get_way_node(tg, element, ind)
            way_nodes.append(way_node)
            ind = ind + 1 

    for tg in element.iter("tag"):
        node_tag = get_node_tag(tg, element)
        if node_tag:
            tags.append(node_tag)

    if fixer: 
        tags = fixer.fix(tags)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def valid_element(element, validator, schema=SCHEMA):
    """Raise warning if element does not match schema"""
    valid = True
    if validator.validate(element, schema) is not True:
        valid = False
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        warnings.warn(message_string.format(field, "\n".join(error_strings)))
    return valid




# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate, strfix_dict, logfile=None):
    """Iteratively process each XML element and write to csv(s)"""

    fixer = fxad.FixAddress(strfix_dict, logfile)


    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = hlp.UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = hlp.UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = hlp.UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = hlp.UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = hlp.UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        validator = cerberus.Validator()

        for element in hlp.get_element(file_in, tags=('node', 'way')):
            try:
                el = shape_element(element, fixer=fixer)
            except Exception as er:
                print "Failed to shape the following element:\n", ET.tostring(element, encoding='utf-8')
                print "Catched Exeption:\n", er
                continue

            if el:
                if validate is True:
                    if not valid_element(el, validator):
                        print "Excluding not valid element:\n", ET.tostring(element, encoding='utf-8')
                        continue

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a smallgf
    # sample of the map when validating.
    
    logfile = "openstrmap\\log_smpl\\fixaddr.log"
    hlp.create_path(logfile)
    
    OSM_PATH = "data\\sample.osm"
    #OSM_PATH = "data\\prague_czech-republic.osm\\prague_czech-republic.osm"
    
    # Log file containig mistyped street names, this list is used for furhter correction
    strfix_dict = "openstrmap\\log\\audit_strnames.log" 
    
    start = time() 
    process_map(OSM_PATH, strfix_dict=strfix_dict, validate=True, logfile=logfile)
    elapsed = time() - start
    print "Estimated time: ", hlp.pretty_time(elapsed) 
