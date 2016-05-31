#Prague OpenStreetMap Project

In this project I am considering map data for Prague, Czech Republic.

House numbering system in Czech Republic is quite complicated, two numbering systems are used concurrently.
The basic house number is the "old" or "descriptive number" . The descriptive number is unique within the municipal part (a village, a quarter, mostly for one cadastral area) or within a whole small municipality. In most cities there are used also the "new" or "orientation numbers". The orientation numbers are arranged sequentially within the street or square. If the building is on a corner or has two sides, it can have two or more orientation numbers, one for each of the adjacent streets or squares. Typical house number in Prague contains two numbers, which are written devided by slash, e.g. 593/5.


https://wiki.openstreetmap.org/wiki/Template:CzechAddress
https://wiki.openstreetmap.org/wiki/Cs:WikiProject_Czech_Republic/Address_system
https://en.wikipedia.org/wiki/House_numbering


Small test dataset of Prague city region were downloaded via Overpass API, latitude in range (50.059973,50.090490) and longitude in (14.417687,14.482060).  

Three main audit procedures related to address data were considered:
- Audit of house numbers
- Audit of street names
- Audit of postcodes


###Audit Address: House Numbers


  Looks like two different addresses for the same element 

```sh
296510460	addr	uir_adr	source
296510460	conscriptionnumber	134;1301	addr
296510460	housenumber	134/16;1301/4	addr
296510460	place	Krč	addr
296510460	postcode	14000	addr
296510460	ruian:addr	28039203	ref
296510460	street	Na Strži;Panuškova	addr
296510460	streetnumber	16;4	addr
296510460	uir_adr:ADRESA_KOD	21859141	regular
```

Inappropriate type of housenumber, looks like the order is incorrect

```sh
2197125390  housenumber 2a/1689 addr
2197125390  name  mBank regular
2197125390  postcode  14000 addr
2197125390  street  Hvězdova  addr
```


Housenumber contains only street number

```sh
296550228	addr	uir_adr	source
296550228	conscriptionnumber	1008	addr
296550228	housenumber	22	addr
296550228	name	Hostel One Home	regular
296550228	postcode	11000	addr
296550228	street	Hybernská	addr
296550228	streetnumber	22	addr
296550228	tourism	hostel	regular
296550228	uir_adr:ADRESA_KOD	21708274	regular
```

Missed housenumber

key addr:housenumber can be missed even if some other information is given.
Possible values for key addr:housenumber:
 - conscriptionnumber / streetnumber
 - conscriptionnumber
 - streetnumber
 - provisionalnumber
 - provisionalnumber / streetnumber

If any information about conscriptionnumber, streetnumber, provisionalnumber is given, 
then it should also be presented as housenumber.

In the following example housenumber is missed and should be added as 
housenumber = streetnumber
```sh
454513743	street	Podle Náhonu	addr
454513743	streetnumber	6	addr
```

Another variant is that housnumber is presented, but it is not complete

```sh
296550228 conscriptionnumber  1008
296550228 housenumber 22
296550228 streetnumber  22
```
In this situation housenumber should be housenumber = 1008/22

####Audit House Number Strategy
 - Validity
 	- Both conscriptionnumber and provisionalnumber are given
 	- Not valid type of housenumber
 	- Not valid type of streetnumber
 	- Not valid type of conscriptionnumber or provisionalnumber
 - Completeness
	- Missed housenumber
	- Missed first number (conscriptionnumber | provisionalnumber),streetnumber or both
	- Missed first number (conscriptionnumber | provisionalnumber) or streetnumber in housenumber
 - Consistency
	- Composite hsnumber is not consistent with first number (conscriptionnumber | provisionalnumber) and streetnumber
	- One-number hsnumber is not consistent with first number (conscriptionnumber | provisionalnumber) or streetnumber

####Fixing House Number Strategy
 - Fix Completeness problems
	- Complete housenumber
	Complete housenumber from given first number (conscriptionnumber | provisionalnumber) and streetnumber
    - Add first number (conscriptionnumber | provisionalnumber) and streetnumber if they are missed

###Audit Address: Street Names

Most street names contain special Czech symbols, for example: Francouzská, Na Louži.
Quite often people use only latin letters in short texts, sms, etc. In this situation above
examples will become Francouzska, Na Louzi. We will check street names on these common mistypes. 

The following function compare two street names and defines if these streets are different, but only in the sense of common czech/latin mistypes.
```python
def is_equalmstp(strname1, strname2):
    cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', \
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', \
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}

    trf = lambda s: cz_subst.get(s) if cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1] == [trf(s) for s in strname2]):
        return True
    else:
        return False 
```
Function checks if latin versions of two street names are equal while not-latin are not. The list of all street names were constructed, then all possible misspeled cases were identified. Actually there are examples of streets which are equal in described scence, but in reality are different streets.   
As additional check we will use postcodes. If two different street names have the same latin spelling and the same postcodes, then proably one street name is misspelled. 
```sh
Nitranská, Nitranska
Národní, Narodni
```
Which street name from the pair is misspelled? We will assume this to the one which has lower number of special Czech symbols.

Two street name fiels can have the same spelling, but different case. It is quite common situation for street names which consists of more than one word: all words can start with upper case letter; only the first word starts with upper case letter and etc.

```sh
náměstí Míru, Náměstí Míru
K vodě, K Vodě
``` 
All street names should be presented in unified format. All words in street name will start with upper case letter.

####Fixing Street Names Strategy
 - All street names should be presented in unified format. All words in street name will start with upper case letter.
 - Fix mistyped street names (from log file)


###Audit Address: Postcodes
In Prague poscodes have 5 digits and start from 1, second digit defines dictict of the city. 
For example address with postcode 12000 is in the city district "Prague 2". However there
 are some non-Prague postcodes, which correspond to villages close to the city. 
 
 ```sh
 CZ - 130 00
 12000 Praha 7
 1051
 ```

Audit Report
```sh
Audit House Numbers
******************************
{'Both cnsnumber and prvnumber are given': 1,
 'Incomplete hsnumber': 11,
 'Inconsistent hsnumber': 13,
 'Missed fstnumber, streetnumber or both': 428,
 'Missed hsnumber': 73,
 'Missed streetnumber or fstnumber in hsnumber': 12,
 'Not valid type of housenumber': 55}
Estimated time:  0h 2min 48sec 864mls
None
Audit Street Names
******************************
{'Mistyped street names': 8, 'Problem chars in street name': 9}
Estimated time:  0h 59min 15sec 378mls
None
Audit Postcodes
******************************
{'Wrong type for post code': 7}
Estimated time:  0h 2min 8sec 378mls
```

Example Data Report
Audit House Numbers
******************************
{'COMPLETENESS: Missed fstnumber, streetnumber or both': 85,
 'COMPLETENESS: Missed hsnumber': 2,
 'COMPLETENESS: Missed streetnumber or fstnumber in hsnumber': 3,
 'VALIDITY: Not valid type of housenumber': 5,
 'VALIDITY: Not valid type of streetnumber': 1}
Estimated time:  0h 7min 49sec 473mls
None
Audit Street Names
******************************
{'Mistyped street names': 1}
Estimated time:  0h 0min 8sec 901mls
None
Audit Postcodes
******************************
{'Wrong type for post code': 5}
Estimated time:  0h 0min 5sec 890mls
None

All Data Report
Audit House Numbers
******************************
{'COMPLETENESS: Missed fstnumber, streetnumber or both': 428,
 'COMPLETENESS: Missed hsnumber': 66,
 'COMPLETENESS: Missed streetnumber or fstnumber in hsnumber': 11,
 'CONSISTENCY: Composite hsnumber is not consistent with fstnumber and streetnumber': 12,
 'CONSISTENCY: One-number hsnumber is not consistent with fstnumber or streetnumber': 8,
 'VALIDITY: Not valid type of conscriptionnumber or provisionalnumber': 8,
 'VALIDITY: Not valid type of housenumber': 55,
 'VALIDITY: Not valid type of streetnumber': 14,
 'VALIDITY:Both cnsnumber and prvnumber are given': 1}
Estimated time:  1h 27min 32sec 793mls
None
Audit Street Names
******************************
{'Mistyped street names': 8}
Estimated time:  0h 39min 21sec 296mls
None
Audit Postcodes
******************************
{'Wrong type for post code': 7}
Estimated time:  0h 2min 8sec 256mls
None






