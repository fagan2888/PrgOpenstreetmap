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




# def test_change_tags_1():
# 	key_values = {
# 		"housenumber" : "100/10",
# 		"streetnumber" : "10",
# 		"conscriptionnumber" : "100"
# 	}

# 	new_tags = fixad.change_tags(tags1, key_values)

# 	assert_equal(new_tags, chktags1)

# def test_change_tags_2():
	
# 	key_values = {
# 		"housenumber" : "ev.100/10",
# 		"streetnumber" : "10",
# 		"provisionalnumber" : "100"
# 	}

# 	new_tags = fixad.change_tags(tags2, key_values)

# 	assert_equal(new_tags, chktags2)	

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
		



