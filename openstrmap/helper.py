 # This Python file uses the following encoding: utf-8

import xml.etree.cElementTree as ET
import codecs 
import sys
import logging
import os
import errno
from collections import namedtuple
import csv



class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_logger(logfile):
    """ Configure and return logger """
    formatter = logging.Formatter('%(asctime)s %(message)s')
    logname = os.path.split(logfile)[-1].split('.')[0]
    logger = logging.getLogger(logname)
    hdlr = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger

def create_path(filepath):
    """ Create specified file path if not exists """
    path = os.path.dirname(filepath)
    try: 
        os.makedirs(path)
    except OSError as exc:
        if (exc.errno != errno.EEXIST) and os.path.isdir(path):
            raise

        
def pretty_time(time):
    """ Return time in specified format: #hours #minutes #seconds #mls """
    time_mls = int(time * 1000)
    hours= time_mls//(1000*60*60)
    minutes=(time_mls//(1000*60)) % 60
    seconds=(time_mls//1000) % 60
    mls = time_mls % 1000
    return "{}h {}min {}sec {}mls".format(hours, minutes, seconds, mls)

def get_element(osm_file, tags=None):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        in_tags = True
        if tags:
            in_tags = elem.tag in tags
        if event == 'end' and in_tags:
            yield elem
            root.clear()

def get_tags_data(element, keys):
    """ Iterate on all element tags and return a tuple with values which correspond to
        specified keys.

        Args:
        element (ET.Element): XML element 
        keys: list of tuples, each tuple includes all keys which define a value to be included in
        final result

        Returns:
        A tuple of length len(keys), each value correspond to specified key(s)
    """
    values = [None] * len(keys)

    for tg in element.iter('tag'):
        kval = tg.attrib["k"]
        value = tg.attrib["v"]

        for i, key in enumerate(keys):
            if any([kval == k for k in key]):
                values[i] = value
    
    return tuple(values)

def get_tags_values(tags, keys):
    """ Iterate on a list of dictionaries and return a tuple with values which correspond to
        specified keys. Each dictionary in input list should have elements {'key': ..., 'value': ...}.

    """
    
    values = [None] * len(keys)
    for tg in tags:
        kval = tg["key"]
        value = tg["value"]

        for i, key in enumerate(keys):
            if any([kval == k for k in key]):
                values[i] = value
    
    return tuple(values)

def change_tags(tags, key_values):
    """ Take a list of dictionaries of format {'key': ..., 'value': ...} and change 'value' values
        using 'key' values and specified key_values dictionary. 
    """
    ntags = tags
    for key, value in key_values.items():
        found = False
        for tg in ntags:
            if tg["key"] == key:
                found = True
                tg["value"] = value
        if not found and value:
            new_tg = {"id" : tags[0]["id"], "key" : key, "type" : "addr", "value" : value }
            ntags.append(new_tg)
    return ntags

AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')

def addr_dict(addr):
    keys = ('housenumber', 'conscriptionnumber', 'provisionalnumber', 'streetnumber')
    return dict(zip(keys, addr))

# A dictionary with common Czech mistypes, format Czech symbol : Latin symbol
cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', \
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', \
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}

def capitalize(line):
    """ Capitalize first letters of all words in a line """
    words = line.lower().split(' ')
    nwords = []
    for i, word in enumerate(words):
        nwords.append("")
        for j, s in enumerate(word):
            ns = s
            if j==0: # Firts letter in a word
                ns = s.upper()
            nwords[i] += ns
    return ' '.join(nwords)

def create_sample_file(datafile, samplefile, n):
    """
    Create sample data file and writes every n elemnt from datafile 
    """
    with open(samplefile, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every 10th top level element
        for i, element in enumerate(get_element(datafile)):
            if i % n == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')

def get_cond_elements(inp_file, min_numlines, max_numlines, conditions):
    """ Return a list of elements (in a string format), which have secondary tags
        with key attribute meeting one of specified conditions. Number of elements 
        for each condition should be between min_numlines and max_numlines
    """
    line_counts = [0] * len(conditions)  #list of number of found lines for each condition
    lines = []
    ids = set()

    for element in get_element(inp_file):
        idval = element.attrib["id"]
        for tg in element.iter('tag'):
            kval = tg.attrib["k"]
            for i, condition in enumerate(conditions):
                if line_counts[i] >= max_numlines:
                    continue 
                if condition(kval) & (idval not in ids):
                    line_counts[i] += 1
                    lines.append(ET.tostring(element))
                    ids.add(idval) 
            if (min(line_counts) >= min_numlines):
                return lines        
    return lines






