# coding: utf-8

import xml.etree.cElementTree as ET
import pprint as pp
import re
from time import time
from collections import defaultdict
import  openstrmap.helper as hlp 
from collections import namedtuple

def count_tags(element, counts):
    """ Count number of elemensts of specified tag """
    tag = element.tag
    counts[tag] = counts[tag] + 1
    return counts


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def audit_key_type(element, keys):
    """ Count number of tag key attributes which contain defined problem chars and colons """
    if element.tag == "tag":
        k_val = element.attrib["k"]
        lbls = [ "lower_colon" ,"lower"]
        ptns = [lower_colon, lower]
        if problemchars.findall(k_val):
            keys["problemchars"] = keys["problemchars"] + 1
            return keys
        for i, ptn in enumerate(ptns): 
            if ptn.match(k_val):
                lbl = lbls[i]
                keys[lbl] = keys[lbl] + 1
                return keys
        
        keys["other"] = keys["other"] + 1
        
    return keys



class   DataAuditor(object):

    def __init__(self, auditors = None, names = None):
        self._auditors = list()
        self._names = list()
        if auditors is not None:
            self._auditors += auditors
        if names is not None:
            self._names += names

    def audit(self, filename):
        timing = {key : 0 for key in self._names}
        audit_result = {name: defaultdict(int) for name in self._names }
        for element in hlp.get_element(filename):
            for i, auditor in enumerate(self._auditors):
                name = self._names[i]
                start = time()
                prev_res = audit_result[name]
                audit_result[name] = auditor(element, prev_res)
                timing[name] = timing[name] + (time() - start)

        return audit_result, timing


if __name__ == "__main__":
    inp_file = "data\\sample.osm"
    
    auditor = DataAuditor([count_tags, audit_key_type], ["count_tags", "audit_key_type"])
    audit_result, timing = auditor.audit(inp_file)
    separator = "***********************************"
    print "Audit Report"
    print separator
    for audit_type, result in audit_result.items():        
        print audit_type
        print separator
        pp.pprint({k: v for k,v in result.items()}, width=1)
        print "Estimated time: ", hlp.pretty_time(timing[audit_type])
        print separator




