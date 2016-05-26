# coding: utf-8

import xml.etree.cElementTree as ET
import pprint as pp
import re
import os
from time import time
from collections import defaultdict, namedtuple
import helper as hlp 


def add_stat(logger, stats, msg, tag, id, info):
    logfmt = u"{} ({},{}): {}"
    if logger:
        line = logfmt.format(msg, tag, id, info)
        logger.info(line)
    stats[msg] += 1

def get_addrnum(element):
    AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')
    addr = AddrNum._make(hlp.get_tags_data(element, [('addr:housenumber', 'housenumber'), \
                                                                      ('addr:conscriptionnumber', 'conscriptionnumber'), \
                                                                      ('addr:provisionalnumber', 'provisionalnumber'), \
                                                                      ('addr:streetnumber', 'streetnumber') \
                                                ]) \
                        )
    return addr

def get_fstnumber(addr):
    fstnumber = None
    if addr.cnsnumber:
        fstnumber = addr.cnsnumber
    if addr.prvnumber:
        fstnumber = addr.prvnumber
    return fstnumber

def chk_valid(addr):
    strpatt = r'^[1-9][0-9]*[a-zA-Z]?$'
    fstpatt = r'^[1-9][0-9]*$'
    hsnpatt =r'^(?:ev.)?(fstpatt)/(strpatt)$|^(?:ev.)?(fstpatt)$|^(strpatt)$'
    #replace with re expessions without first and last symbols, which indicate
    #beginnning and ending of the line
    hsnpatt = hsnpatt.replace('fstpatt', fstpatt[1:-1])
    hsnpatt = hsnpatt.replace ('strpatt', strpatt[1:-1])

    msges = []
    valid = True

    if addr.cnsnumber and addr.prvnumber:
        valid = False
        msges.append("VALIDITY:Both cnsnumber and prvnumber are given")

    fstnumber = get_fstnumber(addr)
    if addr.hsnumber and not re.match(hsnpatt, addr.hsnumber):
        valid = False
        msges.append("VALIDITY: Not valid type of housenumber")
        
    if addr.streetnumber and not re.match(strpatt, addr.streetnumber):
        valid = False
        msges.append("VALIDITY: Not valid type of streetnumber")

    if fstnumber and not re.match(fstpatt, fstnumber):
        valid = False
        msges.append("VALIDITY: Not valid type of conscriptionnumber or provisionalnumber")

    return valid, msges        

def chk_complete(addr):
    msges = []
    valid = True
    if any(addr) and not addr.hsnumber:
            valid = False
            msges.append("COMPLETENESS: Missed hsnumber")
    
    fstnumber = get_fstnumber(addr)
    if addr.hsnumber:
        if ("/" in addr.hsnumber):
            if not all ([fstnumber, addr.streetnumber]):
                valid = False
                msges.append("COMPLETENESS: Missed fstnumber, streetnumber or both")
        else:
            if all([addr.streetnumber, fstnumber]):
                valid = False
                msges.append("COMPLETENESS: Missed streetnumber or fstnumber in hsnumber")
    return valid, msges            

def chk_consist(addr):
    msges = []
    valid = True
    
    fstnumber = get_fstnumber(addr)
    if addr.hsnumber:
        if ("/" in addr.hsnumber) and all([fstnumber, addr.streetnumber]):
            chk_fstnumber, chk_streetnumber = addr.hsnumber.replace('ev.','').split("/")
            if (chk_fstnumber != fstnumber) or (chk_streetnumber != addr.streetnumber):
                valid = False
                msges.append("CONSISTENCY: Composite hsnumber is not consistent with fstnumber and streetnumber")
            
        if ("/" not in addr.hsnumber) and not all([fstnumber, addr.streetnumber]):
            if (fstnumber and (addr.hsnumber.replace('ev.','') != fstnumber)) or \
                   (addr.streetnumber and (addr.hsnumber != addr.streetnumber)):
                valid = False
                msges.append("CONSISTENCY: One-number hsnumber is not consistent with fstnumber or streetnumber")
                    
    return valid, msges

def audit_addrnum(filename, logfile=None):
    stats = defaultdict(int)
        
    logger = hlp.get_logger(logfile) if logfile else None
    
    for element in hlp.get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = get_addrnum(element)

        #Check if any address numbers are given
        if not any(addr):
            continue
 
        valid, msges = chk_valid(addr)
        if not valid:
            for msg in msges:
                add_stat(logger, stats, msg, element.tag, id, addr)
            continue

        for chk in [chk_complete, chk_consist]:
            valid, msges = chk(addr)
            if not valid:
                for msg in msges:
                    add_stat(logger, stats, msg, element.tag, id, addr)
       
    return stats

def is_equallw(strname1, strname2):
    if (strname1 != strname2) and (strname1.lower() == strname2.lower()):
        return True
    else:
        return False

def is_equalmstp(strname1, strname2):
    trf = lambda s: hlp.cz_subst.get(s) if hlp.cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1] == [trf(s) for s in strname2]):
        return True
    else:
        return False  


def chk_valid_strname(strname):
    msges = []
    valid = True

    str_problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,]')
    if str_problemchars.findall(strname):
        msges.append("Problem chars in street name")

    return valid, msges

def audit_strnames(filename, logfile=None):
    logger = hlp.get_logger(logfile) if logfile else None
    strnames = set() 
    stats = defaultdict(int)

    for element in hlp.get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        strname, pcode = hlp.get_tags_data(element, [('addr:street', 'street'), ('addr:postcode', 'postcode')])
        if strname:
            valid, msges = chk_valid_strname(strname)
            if not valid:
                for msg in msges:
                    add_stat(logger, stats, msg, element.tag, id, strname)
            strnames.add((strname, pcode))

    
    strnames = list(strnames)
    for i, name1 in enumerate(strnames):
        for name2 in strnames[i+1:]:
            if is_equalmstp(name1[0], name2[0]) and (name1[1]==name2[1]):
                msg = "Mistyped street names"
                add_stat(logger, stats, msg, None, None, u'({},{}), pcode = {}'.format(name1[0], name2[0], name1[1]) )
            # if is_equallw(name1, name2):
            #      msg = "Capital Lower letters Difference"
            #      add_stat(None, stats, msg, None, None, u'({},{})'.format(name1, name2))  #do not log these cases

    return stats

def audit_postcodes(filename, logfile=None):
    stats = defaultdict(int)
    logger = hlp.get_logger(logfile) if logfile else None
    patt = r'^[1-9][0-9]{4}$'    
        
    for element in hlp.get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        pcode, = hlp.get_tags_data(element, [('addr:postcode', 'postcode')])
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
    else:
        map(hlp.create_path, logfiles) 
    if not headings:
        headings = [None]*len(auditor)
    for i, auditor in enumerate(auditors):
        start = time()
        stats = auditor(filename, logfiles[i])
        elapsed = time() - start
        print headings[i]
        print "******************************"
        pp.pprint(dict(stats))
        print "Estimated time: ", hlp.pretty_time(elapsed) 



if __name__ == "__main__":
    inp_file = "..\\data\\prague_czech-republic.osm\\prague_czech-republic.osm"
    inp_ex_file = "..\\data\\example.osm"
    sample_file = "..\\data\\sample.osm"
    
    #Create sample file if not exist
    if not os.path.exists(sample_file):
        hlp.create_sample_file(inp_file, sample_file, 175)


    process(inp_file, [audit_addrnum, audit_strnames, audit_postcodes],
                       ['log\\audit_addrnum.log', 'log\\audit_strnames.log', 'log\\audit_postcodes.log' ],
                       ['Audit House Numbers', 'Audit Street Names', 'Audit Postcodes'])
    