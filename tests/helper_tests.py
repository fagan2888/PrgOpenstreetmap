# encoding: utf-8

from nose.tools import *
import openstrmap.helper as hlp

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

def test_change_tags_1():
	key_values = {
		"housenumber" : "100/10",
		"streetnumber" : "10",
		"conscriptionnumber" : "100"
	}

	new_tags = hlp.change_tags(tags1, key_values)

	assert_equal(new_tags, chktags1)

def test_change_tags_2():
	
	key_values = {
		"housenumber" : "ev.100/10",
		"streetnumber" : "10",
		"provisionalnumber" : "100"
	}

	new_tags = hlp.change_tags(tags2, key_values)

	assert_equal(new_tags, chktags2)	

def test_capitalize():
	line1 = 'gdfj Afghjsd 5yj'
	chkline1 = 'Gdfj Afghjsd 5yj'
	line2 = 'g'
	chkline2 = 'G'
	line3 = 'Francouzská'
	chkline3 = 'Francouzská'

	nline1 = hlp.capitalize(line1)
	nline2 = hlp.capitalize(line2)
	nline3 = hlp.capitalize(line3)

	assert_equal(nline1, chkline1)
	assert_equal(nline2, chkline2)
	assert_equal(nline3, chkline3)

