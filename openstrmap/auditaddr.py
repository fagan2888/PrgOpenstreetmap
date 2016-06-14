# coding: utf-8

import xml.etree.cElementTree as ET
import pprint as pp
import re
import os
from time import time
from collections import defaultdict, namedtuple
import openstrmap.helper as hlp 


def add_stat(logger, stats, msg, tag, id, info):
    """ Add message to statistics dictionary, add info message to log if given"""
    logfmt = u"{} ({},{}): {}"
    if logger:
        line = logfmt.format(msg, tag, id, info)
        logger.info(line)
    stats[msg] += 1

def get_addrnum(element):
    """ Return address tuple for a given element """
    AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')
    addr = AddrNum._make(hlp.get_tags_data(element, [('addr:housenumber', 'housenumber'), \
                                                                      ('addr:conscriptionnumber', 'conscriptionnumber'), \
                                                                      ('addr:provisionalnumber', 'provisionalnumber'), \
                                                                      ('addr:streetnumber', 'streetnumber') \
                                                ]) \
                        )
    return addr

def get_fstnumber(addr):
    """ Return  cnsnumber or prvnumber in given address tuple. Both cnsnumber
        and cnsnumber can not be included in valid address tuple.
    """
    fstnumber = None
    if addr.cnsnumber:
        fstnumber = addr.cnsnumber
    if addr.prvnumber:
        fstnumber = addr.prvnumber
    return fstnumber

def chk_valid(addr):
    """ Check validity of given address house numbers 

        Args:
            addr: a namedtuple containing hsnumber, cnsnumber, prvnumber, streetnumber

        Returns:
            bool: True if valid, False otherwise.
            list of strings: a list of error messages, empty list if address is valid
    """
    strpatt = r'^[1-9]\d*[a-zA-Z]?$'
    fstpatt = r'^[1-9]\d*$'
    hsnpatt =r'^(?:ev.)?(fstpatt)/(strpatt)$|^(?:ev.)?(fstpatt)$|^(strpatt)$'
    #replace with re expessions without first and last symbols, which indicate
    #beginning and ending of the line
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
    """ Check completeness of given address house numbers 

        Args:
            addr: a namedtuple containing hsnumber, cnsnumber, prvnumber, streetnumber

        Returns:
            bool: True if complete, False otherwise.
            list of strings: a list of error messages, empty list if address is complete
    """
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
    """ Check consistency of given address house numbers 

        Args:
            addr: a namedtuple containing hsnumber, cnsnumber, prvnumber, streetnumber

        Returns:
            bool: True if consistent, False otherwise.
            list of strings: a list of error messages, empty list if address is consistent
    """

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
    """ Audit address house numbers, check validity, completeness and consistency """
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
    """ Check if two street names are different only in letter case """
 
    if (strname1 != strname2) and (strname1.lower() == strname2.lower()):
        return True
    else:
        return False

def is_equalmstp(strname1, strname2):
    """ Check if two street names are different only because of mistypes """
   
    trf = lambda s: hlp.cz_subst.get(s) if hlp.cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1] == [trf(s) for s in strname2]):
        return True
    else:
        return False  


def chk_valid_strname(strname):
    """ Check street name validity """
    msges = []
    valid = True

    str_problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,]')
    if str_problemchars.findall(strname):
        msges.append("Problem chars in street name")

    return valid, msges

def audit_strnames(filename, logfile=None):
    """ Audit street names, check validity and mistypes """
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
            if is_equallw(name1[0], name2[0]):
                 msg = "Capital Lower letters Difference"
                 # This case is not logged
                 add_stat(None, stats, msg, None, None, u'({},{})'.format(name1, name2))  #do not log these cases

    return stats

def chk_valid_postcode(pcode):
    """ Check validity of given postcode """
    msges = []
    valid = True
    patt = r'^[1-9]\d{4}$'

    pcode_strp = pcode.replace(" ", "")
    
    if re.match(patt, pcode_strp):
        pcode_int = int(pcode_strp)
        if not (pcode_int <=  79899 and pcode_int >= 10000): #postcodes range in CZ
            msges.append("Wrong range for post code")
            valid = False
        elif pcode_strp != pcode:
            msges.append("Valid postcode has extra spaces")
            valid = False
    else:
        msges.append("Wrong type for post code")
        valid = False
            
    return valid, msges

def audit_postcodes(filename, logfile=None):
    """ Audit postcodes, check validity """
    stats = defaultdict(int)
    logger = hlp.get_logger(logfile) if logfile else None
    
        
    for element in hlp.get_element(filename, tags=('node', 'way')):
        id = element.attrib["id"]
        pcode, = hlp.get_tags_data(element, [('addr:postcode', 'postcode')])
        if pcode:
            valid, msges = chk_valid_postcode(pcode)
            if not valid:
                for msg in msges:
                    add_stat(logger, stats, msg, element.tag, id, pcode)
                
    return stats



   
def process(filename, auditors, logfiles=None, headings=None):
    """ Process XML file and run audit procedures specified in auditors list"""
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
    inp_file = "data\\sample.osm"
    create_sample_file = False
    #inp_file = "data\\prague_czech-republic.osm\\prague_czech-republic.osm"
    
    if create_sample_file:
        if not os.path.exists(sample_file):
            hlp.create_sample_file(inp_file, sample_file, 175)

    process(inp_file, [audit_addrnum, audit_strnames, audit_postcodes],
                       ['openstrmap\\log_smpl\\audit_addrnum.log', 'openstrmap\\log_smpl\\audit_strnames.log', 'openstrmap\\log_smpl\\audit_postcodes.log' ],
                       ['Audit House Numbers', 'Audit Street Names', 'Audit Postcodes'])

    