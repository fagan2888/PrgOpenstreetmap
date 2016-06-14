# encoding: utf-8

import auditaddr as ad
import openstrmap.helper as hlp
import re
import codecs


class FixAddress:
    def __init__(self, strn_fixfile=None, logfile=None):
        self.strn_fixdict = None
        if strn_fixfile:
            self.strn_fixdict = self.create_strn_fixdict(strn_fixfile)
        
        self.logger = hlp.get_logger(logfile) if logfile else None
    

        
        
    def create_strn_fixdict(self, fixfile):
        """ Parse audit log file and return a dictionary with format {mistyped street name : correct street name} """
        
        fixing_dict = {}
        patt = r'Mistyped street names \(\S*,\S*\): \((\S+),(\S+)\)'
        with codecs.open(fixfile, encoding='utf-8') as f:
            for line in f.readlines():
                m = re.search(patt, line)
                if m:
                    strname1, strname2 = m.groups()
                    mstp_strname, new_strname = self.fix_mstp_strname(strname1, strname2)
                    fixing_dict[mstp_strname] = new_strname
        
        return fixing_dict

    def fix_mstp_strname(self, strname1, strname2):
        """ Take two steet names and define which one is mistyped. Return a pair of street 
            names where the first one is mistyped and the second one is correct.
        """
        cz_symb = hlp.cz_subst.keys()
        cznum1 = sum([1 for s in strname1.lower() if s in cz_symb])
        cznum2 = sum([1 for s in strname2.lower() if s in cz_symb])
        if cznum1 > cznum2:
            mstp_strname = strname2
            new_strname = strname1
        else:
            mstp_strname = strname1
            new_strname = strname2

        return mstp_strname, new_strname

    def has_address(self, tags):
        addr = hlp.get_tags_values(tags, [('housenumber',), ('conscriptionnumber',), \
                                          ('provisionalnumber',), ('streetnumber',), \
                                          ('street',), ('postcode',) \
                                        ])
        return any(addr)

    def fix(self, tags):
        """ Fix house numbers, street names and postcodes """
        if not self.has_address(tags):  
            return tags
        
        tags = self.fix_hsnumber(tags)
        tags = self.fix_strname(tags)
        tags = self.fix_postcodes(tags)

        return tags

    def fix_postcodes(self, tags):
        """ Fix postcodes: remove spaces in valid postcodes, extract valid postcode from the text """
        patt = r'^(?:.*\D)?([1-9]\d{4})(?:\D.*)?$'
        ntags = tags
    
        (pcode,) = hlp.get_tags_values(tags, [("postcode",)])
        if not pcode:
            return tags

        valid, msges = ad.chk_valid_postcode(pcode)
        if not valid:
            pcode_strp = pcode.replace(" ", "")
            if msges == ["Valid postcode has extra spaces"]:
                # Replace spaces 
                ntags = hlp.change_tags(tags, {"postcode" : pcode_strp})
                if self.logger:
                        self.logger.info(u"Remove Spaces from Postcode: {} replaced with {}}".format(pcode, pcode_strp))
            else: 
                new_pcode = re.findall(patt, pcode_strp)
                if new_pcode:
                    ntags = hlp.change_tags(tags, {"postcode" : new_pcode[0]})
                    if self.logger:
                        self.logger.info(u"Fix Postcode: {} replaced with {}}".format(pcode, new_pcode[0]))
                        
        return ntags

    def fix_strname(self, tags):
        """ Fix street name mistypes and uniform street name format """
        (strname,) = hlp.get_tags_values(tags, [("street",)])
        if not strname:
            return tags

        nstrname = strname
        mstp_msg = ""
        if self.strn_fixdict and nstrname in self.strn_fixdict:
            nstrname = self.strn_fixdict[nstrname]
            mstp_msg = u"(Mistyped)"

        nstrname = hlp.capitalize(nstrname)
        if strname != nstrname:
            hlp.change_tags(tags, {"street" : nstrname})
            if self.logger:
                self.logger.info(u"Fix Street Name {}: {} replaced with {}".format(mstp_msg, strname, nstrname))
            
        return tags

    def complete_addrnum(self, addr, msges):
        """ Complete address house numbers in order all parts be included:  
            cnsnumber or prvnumber, streetnumber and hsnumber
        """
        (hsnumber, cnsnumber, prvnumber,streetnumber) = addr
        for msg in msges:
            if msg == "COMPLETENESS: Missed hsnumber":
                hsnumber = ""
                if addr.cnsnumber:
                    hsnumber = addr.cnsnumber
                if addr.prvnumber:
                    hsnumber = 'ev.' + addr.prvnumber 
                if addr.streetnumber:
                    if hsnumber:
                        hsnumber = hsnumber + '/' + addr.streetnumber
                    else:
                        hsnumber = addr.streetnumber

            if msg == "COMPLETENESS: Missed fstnumber, streetnumber or both":
                if "/" in addr.hsnumber:
                    first, second = addr.hsnumber.split("/")
                    streetnumber = second
                    if 'ev.' in first:
                        prvnumber = first.replace("ev.","")
                    else:
                        cnsnumber = first

            if msg == "COMPLETENESS: Missed streetnumber or fstnumber in hsnumber":
                if addr.prvnumber and addr.prvnumber != addr.hsnumber:
                    hsnumber = 'ev.' + addr.prvnumber + '/' + addr.hsnumber
                if addr.cnsnumber and addr.cnsnumber != addr.hsnumber:
                    hsnumber = addr.cnsnumber + '/' + addr.hsnumber
                if addr.streetnumber and addr.streetnumber != addr.hsnumber:
                    hsnumber = addr.hsnumber + '/' + addr.streetnumber

        return hlp.AddrNum(hsnumber, cnsnumber, prvnumber,streetnumber)

    def fix_hsnumber(self, tags):
        """ Fix completeness problems in address house numbers """
        addr = hlp.AddrNum._make(hlp.get_tags_values(tags, [('housenumber',), ('conscriptionnumber',), \
                                                    ('provisionalnumber',), ('streetnumber',) \
                                                    ]) \
                            )

        if not any(addr):
            return tags

        ntags = tags
        valid,_ = ad.chk_valid(addr)
        if valid:
            compl, msges = ad.chk_complete(addr)
            if not compl:
                naddr = self.complete_addrnum(addr, msges)
                if ad.chk_consist(naddr):
                    ntags = hlp.change_tags(tags, hlp.addr_dict(naddr))
                    if self.logger:
                        self.logger.info(u"Fix Address Numbers: \n" + str(tags))
                        self.logger.info("*****************")
                    
        return ntags

    






