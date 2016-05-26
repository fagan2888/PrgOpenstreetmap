 # This Python file uses the following encoding: utf-8

import xml.etree.cElementTree as ET
import codecs 
import sys
import pprint as pp
import re
from time import time
from functools import partial
import logging
import os
import errno
from collections import namedtuple




def get_logger(logfile):
    #logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode='w')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    logname = os.path.split(logfile)[-1].split('.')[0]
    logger = logging.getLogger(logname)
    hdlr = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger

def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))

def get_first_elements (inp_file, num_el):
	with open(inp_file) as f:
		fstline = f.readline()
		sndline = f.readline()

	i = 0 
	lines = []
	lines.append(fstline)
	lines.append(sndline)
	ending = "</osm>"
	iterparser = ET.iterparse(inp_file, events=("start", "end"))
	_,  root = iterparser.next()
	for event, element in iterparser:
		if i > num_el:
			lines.append(ending)
			return lines
		lines.append(ET.tostring(element, encoding="utf-8"))
		i = i + 1
		root.clear()

	lines.append(ending)
	return lines

def create_path(filepath):
	path = os.path.dirname(filepath)
	try: 
		os.makedirs(path)
	except OSError as exc:
		if (exc.errno != errno.EEXIST) and os.path.isdir(path):
			raise

		
def pretty_time(time):
    time_mls = int(time * 1000)
    hours= time_mls//(1000*60*60)
    minutes=(time_mls//(1000*60)) % 60
    seconds=(time_mls//1000) % 60
    mls = time_mls % 1000
    print "{}h {}min {}sec {}mls".format(hours, minutes, seconds, mls)


def get_key_examples(filename, lowcol_file, prch_file):
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

	lowcol = set()
	prch = set()

	kval = ""
	with codecs.open(lowcol_file, "w", encoding = "utf-8") as lcf, codecs.open(prch_file, "w", encoding = "utf-8") as pcf:
		for _, element in ET.iterparse(filename):
			if element.tag == "tag":
				kval = element.attrib["k"]
				if problemchars.findall(kval) :
					if kval not in prch:
						try:
							pcf.write(kval)
							pcf.write('\n')
						except Exception:
							print "Error writing prchars kval to file"
							continue
					prch.add(kval)
	
	    		if lower_colon.match(kval):
					if kval not in lowcol:
						try:
							lcf.write(kval)
							lcf.write('\n')
						except Exception:
							print "Error writing lowcol kval to file"
							continue
					lowcol.add(kval)
					
					

def get_cond_lines(inp_file, min_numlines, max_numlines, conditions):
	
	line_counts = [0] * len(conditions)  #list of number of found lines for each condition
	lines = []

	with open(inp_file) as f:
		for line in f:
			for i, condition in enumerate(conditions):
				if line_counts[i] >= max_numlines:
					continue 
				if condition(line):
					line_counts[i] += 1
					lines.append(line) 
			if (min(line_counts) >= min_numlines):
				return lines		
	return lines

def get_element(osm_file, tags=None):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        in_tags = True
        if tags:
        	in_tags = elem.tag in tags
        if event == 'end' and in_tags:
            yield elem
            root.clear()


###Getting and setting data in tags

def get_tags_data(element, keys):
    #function iterate on all element tags and returns values correspomding to 
    #specified keys.
    #keys - list of tuples, each tuple define possible keys
    #Returns a tuple of values, length = len(keys)
    values = [None] * len(keys)

    for tg in element.iter('tag'):
        kval = tg.attrib["k"]
        value = tg.attrib["v"]

        for i, key in enumerate(keys):
            if any([kval == k for k in key]):
                values[i] = value
    
    return tuple(values)

def get_tags_values(tags, keys):
    values = [None] * len(keys)
    for tg in tags:
        kval = tg["key"]
        value = tg["value"]

        for i, key in enumerate(keys):
            if any([kval == k for k in key]):
                values[i] = value
    
    return tuple(values)

def change_tags(tags, key_values):
    ntags = tags
    for key, value in key_values.items():
        found = False
        for tg in ntags:
            if tg["key"] == key:
                found = True
                tg["value"] = value
        if not found and value:
            new_tg = {"id" : tags[0]["id"], "key" : key, "type" : "addr", "value" : value }
            ntags.append(new_tg)
    return ntags

#################

 ###Address helper functions

AddrNum = namedtuple('AddrNum', 'hsnumber, cnsnumber, prvnumber, streetnumber')

def addr_dict(addr):
    keys = ('housenumber', 'conscriptionnumber', 'provisionalnumber', 'streetnumber')
    return dict(zip(keys, addr))

cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', \
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', \
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}

def capitalize(line):
	words = line.lower().split(' ')
	nwords = []
	for i, word in enumerate(words):
		nwords.append("")
		for j, s in enumerate(word):
			ns = s
			if j==0: # Firts letter in a word
				ns = s.upper()
			nwords[i] += ns
	return ' '.join(nwords)

#################

def create_sample_file(datafile, samplefile, n):
	"""
	Creates sample data file and writes every n elemnt from datafile 
	"""
	with open(samplefile, 'wb') as output:
		output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
		output.write('<osm>\n  ')

    	# Write every 10th top level element
		for i, element in enumerate(get_element(datafile)):
			if i % n == 0:
				output.write(ET.tostring(element, encoding='utf-8'))

		output.write('</osm>')



def get_cond_elements(inp_file, min_numlines, max_numlines, conditions):
	
	line_counts = [0] * len(conditions)  #list of number of found lines for each condition
	lines = []
	ids = set()

	for element in get_element(inp_file):
		idval = element.attrib["id"]
		for tg in element.iter('tag'):
			kval = tg.attrib["k"]
			for i, condition in enumerate(conditions):
				if line_counts[i] >= max_numlines:
					continue 
				if condition(kval) & (idval not in ids):
					line_counts[i] += 1
					lines.append(ET.tostring(element))
					ids.add(idval) 
			if (min(line_counts) >= min_numlines):
				return lines		
	return lines


def get_first_lines(inp_file, num_lines, condition = None):

	lines = []
	with open(inp_file) as f:
		i = 0
		for line in f:
			check = True
			if condition is not None:
				check = condition(line)
			if not check:
				continue
			if i > num_lines:
				return lines
			lines.append(line) 
			i = i + 1
	return lines




if __name__ == "__main__":
	inp_file = "..\\data\\prague_czech-republic.osm\\prague_czech-republic.osm"
	new_file_xml = "..\\data\\prague_czech-republic.osm\\ex.osm"
	new_file = "..\\data\\prague_czech-republic.osm\\outp.osm"
	
#	lowcol, prch = get_key_examples(inp_file)

	# start = time()
	# get_key_examples(inp_file, "lowcol.txt", "prch.txt")
	# print "Elapsed time: ", get_pretty_time(time()-start)
	

	# with open(new_file_xml, "w") as f: 
	# 	#text =  get_first_lines(inp_file, 40)
	# 	text =  get_first_elements(inp_file, 10000)
		
	# 	f.writelines(text)


	condition = lambda line, substr: True if substr in line else False
	# strange_keys = [ 'k=\"name:rmy\"',
	# 					'k=\"name:sah\"',
	# 					'k=\"name:sco\"'
 # 	]

	strange_keys = [ 'k=\"fuel:lpg\"',
						'k=\"fuel:diesel\"',
						'k=\"diet:vegetarian\"',
						'k=\"recycling:wood\"',
						'k=\"recycling:plastic\"',
						'k=\"recycling:batteries\"',
						'k=\"payment:credit_cards\"',
						'k=\"payment:meal_voucher\"'


 	]

 	
 	strange_keys2 = ['maxweight:3.5',
 	 				r'ref:ropiky.net',
 					r'hgv:3.5',
					r'hgv:7.5',
					r'býv.kino',
					r'website:kam.cuni.cz'
	]

 # 	conditions = [partial(condition, substr = key) for key in strange_keys2]
	# with open("prch_ex2.txt", "w") as f: 
		

	# 	text =  get_cond_elements(inp_file, 1, 4, conditions)
		
	# 	f.writelines(text)

	#TO DO:
	# How to pass function with some arguments assigned

