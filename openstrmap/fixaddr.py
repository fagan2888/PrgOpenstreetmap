# encoding: utf-8

import auditaddr as ad
import helper as hlp
import re
import codecs


class FixAddress:
    def __init__(self, strn_fixfile=None, logfile=None):
        self.strn_fixdict = None
        if strn_fixfile:
            self.strn_fixdict = self.create_strn_fixdict(strn_fixfile)
        
        self.logger = hlp.get_logger(logfile) if logfile else None
    

        
        
    def create_strn_fixdict(self, fixfile):
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
                                          ('street',) \
                                        ])
        return any(addr)

    def fix(self, tags):
        
        if not self.has_address(tags):  
            return tags
        
        tags = self.fix_hsnumber(tags)
        tags = self.fix_strname(tags)
        

        return tags

    def fix_strname(self, tags):
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


if __name__ == "__main__":
    fixAddress1 = FixAddress("..\\test_data\\audit_strnames.log")
    tags9 = [
            {"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
            {"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
            {"id": 1, "key": "street", "value" : "Narodni", "type": "addr"}
        ]

    chktags9 = [
            {"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
            {"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
            {"id": 1, "key": "street", "value" : "Národní", "type": "addr"},
            {"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"}
        ]
    
    new_tags9 = fixAddress1.fix(tags9)
    print new_tags9





