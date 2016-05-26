from nose.tools import *
import openstrmap.auditaddr as ad
import openstrmap.helper as hlp
from collections import namedtuple


def test_get_addrnum():
    addr_list = []
    test_filename = 'test_data\\test_data.osm'
    for element in hlp.get_element(test_filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = ad.get_addrnum(element)
        addr_list.append(addr)

    AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')
    assert_equal(addr_list[0], AddrNum(None,None,None,None))
    assert_equal(addr_list[9], AddrNum('15',None,None,None))
    assert_equal(addr_list[10], AddrNum('1265/21','1265',None,'21'))

    

def test_chk_valid():
    test_filename = 'test_data\\test_chk_valid.osm'
    results = []
    for element in hlp.get_element(test_filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = ad.get_addrnum(element)

        valid, msges = ad.chk_valid(addr)
        results.append((valid, msges))

    assert_equal(results[0][0], True )
    assert_equal(results[0][1], [])
    assert_equal(results[11][0], False )
    assert_equal(results[11][1], ["VALIDITY:Both cnsnumber and prvnumber are given", "VALIDITY: Not valid type of housenumber"])
    assert_equal(results[12][0], False )
    assert_equal(results[12][1], ["VALIDITY: Not valid type of streetnumber", "VALIDITY: Not valid type of conscriptionnumber or provisionalnumber"])
    assert_equal(results[9][0], True )
    assert_equal(results[9][1], [])
    assert_equal(results[10][0], True )
    assert_equal(results[10][1], [])
    
def test_chk_complete():
    test_filename = 'test_data\\test_chk_complete.osm'
    results = []
    for element in hlp.get_element(test_filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = ad.get_addrnum(element)

        valid, msges = ad.chk_complete(addr)
        results.append((valid, msges))

    assert_equal(results[9][0], False )
    assert_equal(results[9][1], ["COMPLETENESS: Missed hsnumber"])
    assert_equal(results[10][0], True )
    assert_equal(results[10][1], [])
    assert_equal(results[11][0], False )
    assert_equal(results[11][1], ["COMPLETENESS: Missed fstnumber, streetnumber or both"])
    assert_equal(results[12][0], False )
    assert_equal(results[12][1], ["COMPLETENESS: Missed streetnumber or fstnumber in hsnumber"])
    
    
def test_chk_consist():
    test_filename = 'test_data\\test_chk_consist.osm'
    results = []
    for element in hlp.get_element(test_filename, tags=('node', 'way')):
        id = element.attrib["id"]
        addr = ad.get_addrnum(element)

        valid, msges = ad.chk_consist(addr)
        results.append((valid, msges))

    assert_equal(results[10][0], False )
    assert_equal(results[10][1], ["CONSISTENCY: Composite hsnumber is not consistent with fstnumber and streetnumber"])
    assert_equal(results[11][0], True )
    assert_equal(results[11][1], [])
    assert_equal(results[12][0], False )
    assert_equal(results[12][1], ["CONSISTENCY: One-number hsnumber is not consistent with fstnumber or streetnumber"])
    assert_equal(results[13][0], False )
    assert_equal(results[13][1], ["CONSISTENCY: Composite hsnumber is not consistent with fstnumber and streetnumber"])








    

