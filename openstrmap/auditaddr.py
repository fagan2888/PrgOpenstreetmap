# coding: utf-8

import xml.etree.cElementTree as ET
import pprint as pp
import re
from time import time
from collections import defaultdict, namedtuple
from helper import get_element, pretty_time, get_logger, is_sequence, get_tags_data



def add_stat(logger, stats, msg, tag, id, info):
    logfmt = u"{} ({},{}): {}"
    if logger:
        line = logfmt.format(msg, tag, id, info)
        logger.info(line)
    stats[msg] += 1


    
def audit_addrnum(filename, logfile=None):
    ways_res = defaultdict(list)
    nodes_res = defaultdict(list)

    stats = defaultdict(int)
    AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')
        
    logger = get_logger(logfile) if logfile else None
    
    for element in get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = AddrNum._make(get_tags_data(element, [('addr:housenumber', 'housenumber'), \
                                                                      ('addr:conscriptionnumber', 'conscriptionnumber'), \
                                                                      ('addr:provisionalnumber', 'provisionalnumber'), \
                                                                      ('addr:streetnumber', 'streetnumber') \
                                                    ]) \
                            )

        if addr.cnsnumber and addr.prvnumber:
            msg = "Both cnsnumber and prvnumber are given"
            add_stat(logger, stats, msg, element.tag, id, addr)

        # We will use one variable fstnumber which will be equal to cnsnumber if it is given or 
        # prvnumber if it is given
        fstnumber = None
        if addr.cnsnumber:
            fstnumber = addr.cnsnumber
        if addr.prvnumber:
            fstnumber = addr.prvnumber

            
        strpatt = r'^[1-9][0-9]*[a-zA-Z]?$'
        fstpatt = r'^[1-9][0-9]*$'
        hsnpatt =r'^(?:ev.)?(fstpatt)/(strpatt)$|^(?:ev.)?(fstpatt)$|^(strpatt)$'
        #replace with re expessions without first and last symbols, which indicate
        #beginnning and ending of the line
        hsnpatt = hsnpatt.replace('fstpatt', fstpatt[1:-1])
        hsnpatt = hsnpatt.replace ('strpatt', strpatt[1:-1])



        if addr.hsnumber:

            m = re.match(hsnpatt, addr.hsnumber)
            if not m:
                msg = "Not valid type of housenumber"
                add_stat(logger, stats, msg, element.tag, id, addr)
                continue

            if ("/" in addr.hsnumber):
                if all([fstnumber, addr.streetnumber]):
                    chk_fstnumber, chk_streetnumber = m.groups()[0:2]
                    if (chk_fstnumber != fstnumber) or (chk_streetnumber != addr.streetnumber):
                        msg = "Inconsistent hsnumber"
                        add_stat(logger, stats, msg, element.tag, id, addr)

                if not all ([fstnumber, addr.streetnumber]):
                    msg = "Missed fstnumber, streetnumber or both"
                    add_stat(logger, stats, msg, element.tag, id, addr)
            else:
                if all([addr.streetnumber, fstnumber]):
                    msg = "Missed streetnumber or fstnumber in hsnumber"
                    add_stat(logger, stats, msg, element.tag, id, addr)
                else:
                    if fstnumber and (addr.hsnumber.replace('ev.','') != fstnumber):
                        msg = "Incomplete hsnumber"
                        add_stat(logger, stats, msg, element.tag, id, addr)
                    if addr.streetnumber and (addr.hsnumber != addr.streetnumber):    
                        msg = "Incomplete hsnumber"
                        add_stat(logger, stats, msg, element.tag, id, addr)
        
        
        if any(addr) and not addr.hsnumber:
            msg = "Missed hsnumber"
            add_stat(logger, stats, msg, element.tag, id, addr)
      
    return stats
 
def is_equalmstp(strname1, strname2):
    cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', \
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', \
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}

    trf = lambda s: cz_subst.get(s) if cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1] == [trf(s) for s in strname2]):
        return True
    else:
        return False 

def is_equallw(strname1, strname2):
    if (strname1 != strname2) and (strname1.lower() == strname2.lower()):
        return True
    else:
        return False 


def audit_strnames(filename, logfile=None):
    str_problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,]')
    logger = get_logger(logfile) if logfile else None
    strnames = set() 
    stats = defaultdict(int)

    for element in get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        strname, = get_tags_data(element, [('addr:street', 'street')])
        if strname:
            if str_problemchars.findall(strname):
                msg = "Problem chars in street name"
                add_stat(logger, stats, msg, element.tag, id, strname)
            strnames.add(strname)

    
    strnames = list(strnames)
    for i, name1 in enumerate(strnames):
        for name2 in strnames[i+1:]:
            if is_equalmstp(name1, name2):
                msg = "Mistyped street names"
                add_stat(logger, stats, msg, None, None, u'({},{})'.format(name1, name2) )
            # if is_equallw(name1, name2):
            #     msg = "Capital Lower letters Difference"
            #     add_stat(logger, stats, msg, None, None, u'({},{})'.format(name1, name2))

    return stats

def audit_postcodes(filename, logfile=None):
    stats = defaultdict(int)
    logger = get_logger(logfile) if logfile else None
    patt = r'^[1-9][0-9]{4}$'    
        
    for element in get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        pcode, = get_tags_data(element, [('addr:postcode', 'postcode')])
        if pcode:
            pcode_strp = pcode.replace(" ", "")
            if re.match(patt, pcode_strp):
                pcode = int(pcode_strp)
                if not (pcode <=  79899 and pcode >= 10000): #postcodes range in CZ
                    msg = "Wrong range for post code"
                    add_stat(logger, stats, msg, element.tag, id, pcode)
            else:
                msg = "Wrong type for post code"
                add_stat (logger, stats, msg, element.tag, id, pcode)
    return stats
   
def process(filename, auditors, logfiles=None, headings=None):
    if not logfiles:
        logfiles = [None]*len(auditor)
    if not headings:
        headings = [None]*len(auditor)
    for i, auditor in enumerate(auditors):
        start = time()
        stats = auditor(filename, logfiles[i])
        elapsed = time() - start
        print headings[i]
        print "******************************"
        pp.pprint(dict(stats))
        print "Estimated time: ", pretty_time(elapsed) 



if __name__ == "__main__":
    inp_file = "..\\data\\prague_czech-republic.osm\\prague_czech-republic.osm"
    inp_ex_file = "..\\data\\example.osm"

    # process(inp_file, [audit_strnames, audit_postcodes],
    # 					 ['audit_strnames_all.log', 'audit_postcodes_all.log'],
    # 					 ['Audit Street Names', "Audit Post Codes"])

    process(inp_file, [audit_postcodes],
                         ['audit_postcodes_all.log'],
                         ["Audit Post Codes"])
