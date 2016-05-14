
https://wiki.openstreetmap.org/wiki/Template:CzechAddress
https://wiki.openstreetmap.org/wiki/Cs:WikiProject_Czech_Republic/Address_system


During exploration of small sample of main dataset the following 
problems were identified:

  - House numbers in address
  
    In Prague a house has two numbrers 
        housenumber	496/8,
        the first number is conscriptionnumber, the second - streetnumber.
  
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

##Street names

Most street names contain special Czech symbols, for example: Francouzská, Na Louži.
Quite often people use only latin letters in short texts, sms, etc. In this situation above
examples will become Francouzska, Na Louzi. We will check street names on these common mistypes. 

The following function compare two street names and defines if these streets are different, but only in the sense
 of common czech/latin mistypes and capital/small letters. 

```python
def is_quite_equal(strname1, strname2):
    cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', \
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', \
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}

    trf = lambda s: cz_subst.get(s) if cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1.lower()] == [trf(s) for s in strname2.lower()]):
        return True
    else:
        return False 

```sh
Nitranská, Nitranska
náměstí Míru, Náměstí Míru
K vodě, K Vodě
``` 

The problem of capital/small letters are quite common for street names with more then one word. 
 like á or ě

The following function was



## Audit postcodes
In Prague poscodes have 5 digits and start from 1, second digit defines dictict of the city. 
For example address with postcode 12000 is in the city district "Prague 2". However I have noticed that there
 are a lot of non-Prague postcodes, which correspond to villages close to the city. We will check postcodes to be valid postcode in Prague or 
  Central Bohemian Region (region around Prague). 
  








