# coding: utf-8

from nose.tools import *
import openstrmap.fixaddr as fixad


tags1 = [
			{"id": 1, "key": "housenumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
		]
chktags1 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
		]

tags2 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "provisionalnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
	]
chktags2 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "provisionalnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"},
			{"id": 1, "key": "housenumber", "value" : "ev.100/10", "type": "addr"}
	]

tags3 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
	]
chktags3 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"}
		]

tags4 = [
			{"id": 1, "key": "housenumber", "value" : "ev.100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
	]
chktags4 = [
			{"id": 1, "key": "housenumber", "value" : "ev.100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"},
			{"id": 1, "key": "provisionalnumber", "value" : "100", "type": "addr"}
		]

tags5 = [
			{"id": 1, "key": "housenumber", "value" : "ev.100/10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
	]
chktags5 = [
			{"id": 1, "key": "housenumber", "value" : "ev.100/10", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"},
			{"id": 1, "key": "provisionalnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			
		]


fixAddress = fixad.FixAddress()

def test_fix_hsnumber1():
	new_tags = fixAddress.fix_hsnumber(tags1)
	assert_equal(new_tags, chktags1)

def test_fix_hsnumber2():
	new_tags = fixAddress.fix_hsnumber(tags2)
	assert_equal(new_tags, chktags2)

def test_fix_hsnumber3():
	new_tags = fixAddress.fix_hsnumber(tags3)
	assert_equal(new_tags, chktags3)

def test_fix_hsnumber4():
	new_tags = fixAddress.fix_hsnumber(tags4)
	assert_equal(new_tags, chktags4)

def test_fix_hsnumber5():
	new_tags = fixAddress.fix_hsnumber(tags5)
	assert_equal(new_tags, chktags5)


tags6 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "blabla", "type": "addr"}
		]
chktags6 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Blabla", "type": "addr"}
		]


tags7 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Has Hdfj", "type": "addr"}
		]
chktags7 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Has Hdfj", "type": "addr"}
		]


tags8 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Narodni", "type": "addr"}
		]

chktags8 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Národní", "type": "addr"}
		]

fixAddress1 = fixad.FixAddress("test_data\\audit_strnames")

def test_fix_strname():
	new_tags6 = fixAddress1.fix_strname(tags6)
	new_tags7 = fixAddress1.fix_strname(tags7)
	new_tags8 = fixAddress1.fix_strname(tags8)
		
	assert_equal(new_tags6, chktags6)
	assert_equal(new_tags7, chktags7)
	assert_equal(new_tags8, chktags8)

tags9 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Narodni", "type": "addr"}
		]

chktags9 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Národní", "type": "addr"},
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"}
		]

tags10 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Blabla", "type": "addr"}
		]

chktags10 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Blabla", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"}
			
			]

tags11 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"}
		]

chktags11 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"}
			
			]




def test_fix():
	new_tags9 = fixAddress1.fix(tags9)
	new_tags10 = fixAddress1.fix(tags10)
	new_tags11 = fixAddress1.fix(tags11)

	assert_equal(new_tags9, chktags9)
	assert_equal(new_tags10, chktags10)
	assert_equal(new_tags11, chktags11)

tags12 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Narodni", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "252 28;25228", "type": "addr"}
		]

chktags12 = [
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : u"Národní", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "25228", "type": "addr"},
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"}
		]

tags13 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Blabla", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "120 00", "type": "addr"}
		]

chktags13 = [
			{"id": 1, "key": "housenumber", "value" : "100/10", "type": "addr"},
			{"id": 1, "key": "conscriptionnumber", "value" : "100", "type": "addr"},
			{"id": 1, "key": "street", "value" : "Blabla", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "12000", "type": "addr"},
			{"id": 1, "key": "streetnumber", "value" : "10", "type": "addr"}
			
			
		]

tags14 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "CZ - 130 00", "type": "addr"}
		]

chktags14 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "13000", "type": "addr"}
		]	

tags15 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "Praha 2", "type": "addr"}
		]

chktags15 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "Praha 2", "type": "addr"}
		]

tags16 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "CZ14100", "type": "addr"}
		]

chktags16 = [
			{"id": 1, "key": "hjdsa", "value" : "10", "type": "addr"},
			{"id": 1, "key": "ghs", "value" : "100", "type": "addr"},
			{"id": 1, "key": "postcode", "value" : "14100", "type": "addr"}
			
		]



def test_fix_withpostcodes():
	new_tags12 = fixAddress1.fix(tags12)
	new_tags13 = fixAddress1.fix(tags13)
	new_tags14 = fixAddress1.fix(tags14)
	new_tags15 = fixAddress1.fix(tags15)
	new_tags16 = fixAddress1.fix(tags16)


	assert_equal(new_tags12, chktags12)
	assert_equal(new_tags13, chktags13)
	assert_equal(new_tags14, chktags14)
	assert_equal(new_tags15, chktags15)
	assert_equal(new_tags16, chktags16)
			



