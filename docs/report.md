#Prague OpenStreetsMap Project

###Map Area

Prague, Czech Republic.

https://mapzen.com/data/metro-extracts/ 

In this project I am considering OpenStreetsMap data for Prague, where I have been living for four years.

OSM XML file for the whole area was downloaded via Map Zen interface. Small sample data is provided in '\data\sample.osm'. Some intermediate data files were also used for analysis and were downloaded via Overpass API.

##Data Problems: Audit Address Information

House numbering system in Czech Republic is quite complicated, two numbering systems are used concurrently.
The basic house number is the "old" or "descriptive number" . The descriptive number is unique within the municipal part (a village, a quarter, mostly for one cadastral area) or within a whole small municipality. In most cities there are used also the "new" or "orientation numbers". The orientation numbers are arranged sequentially within the street or square. If the building is on a corner or has two sides, it can have two or more orientation numbers, one for each of the adjacent streets or squares. Typical house number in Prague contains two numbers, which are written divided by slash, e.g. 593/5.

More detailed information can be found here:
https://wiki.openstreetmap.org/wiki/Template:CzechAddress
https://wiki.openstreetmap.org/wiki/Cs:WikiProject_Czech_Republic/Address_system
https://en.wikipedia.org/wiki/House_numbering

It comes as no surprise that a lot of problems and errors were detected in address information.

Three main audit procedures related to address data were considered:
- Audit of house numbers
- Audit of street names
- Audit of postcodes


###Audit House Numbers

Below you can find some examples of problematic data.

In the next example two different addresses were mixed for the same element. This address is not valid. 

|id|key|value|type|
|-----------|--------------|---------------|--------|
|296510460|	conscriptionnumber|	134;1301     |	addr|
|296510460|	housenumber       |	134/16;1301/4|	addr|
|296510460|	postcode	|14000	|addr|
|296510460|	street	|Na Strži;Panuškova	|addr|
|296510460|	streetnumber|	16;4|	addr|


In this example housenumber is not complete and does not include conscriptionnumber, complete housenumber here will be 1008/22

|id|key|value|type|
|-----------|--------------|---------------|--------|
|296550228|	conscriptionnumber|	1008|	addr|
|296550228|	housenumber|	22	|addr|
|296550228|	postcode|	11000|	addr|
|296550228|	street|	Hybernská|	addr|
|296550228|	streetnumber|	22|	addr|

The following checkings were implemented:
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

Audit report for the whole data set:
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
```
Suggested corrections:

 - Fix Completeness problems
	- Complete housenumber
	Complete housenumber from given first number (conscriptionnumber | provisionalnumber) and streetnumber
    - Add first number (conscriptionnumber | provisionalnumber) and streetnumber if they are missed

###Audit Street Names

Most street names contain special Czech symbols, for example: Francouzská, Na Louži.
Sometimes people use only Latin letters in Czech text, for example if they do not have access to Czech keyboard. In this situation above examples will become Francouzska, Na Louzi.

The following is an examples of mistyped street name from the dataset:

```sh
Nitranská, Nitranska
Národní, Narodni
```
First street name in the pair is the right one and the second name is mistyped.

In order to find such cases a list of common mistypes were introduced:

```python
#openstrmap.helper:
cz_subst = {u'á':u'a', u'č':u'c', u'ď':u'd', u'é':u'e', u'ě':u'e', 
             u'í':u'i', u'ň':u'n', u'ó':u'o', u'ř':u'r', u'š':u's', 
              u'ť':u't', u'ů':u'u', u'ý':u'y', u'ž':u'z'}
```

The following function compare two street names and defines if these names can be the same after correction of some common mistypes. In other words it checks if Latin versions of two street names are equal while not-Latin versions are not.
```python
import openstrmap.helper as hlp

def is_equalmstp(strname1, strname2):
    trf = lambda s: hlp.cz_subst.get(s) if hlp.cz_subst.get(s) is not None else s
    if (strname1 != strname2) and ([trf(s) for s in strname1] == [trf(s) for s in strname2]):
        return True
    else:
        return False  

```
All pairs where one street name were probably mistyped were identified. Actually there are examples of street names which can be considered as mistyped according to this logic , but in reality are correct names. As additional check I used postcodes. If two different street names have the same Latin spelling and the same postcodes, then probably one street name was mistyped. 

We will fix these errors and use the right version of a street name. We assume that the right version is the one, which contain more "special Czech symbols". During the audit procedure all these candidates are loged in a separate file, so one can manually check and edit this list before running correction procedures.

Another problem related to street names - different case letters, some examples are presented below:

```sh
náměstí Míru, Náměstí Míru
K vodě, K Vodě
``` 

It is quite common especially for street names which consist of more than one word. We will assume that all words in a street name should start with upper case letters and make corresponding corrections in the data;

Audit report for the whole data set:
```sh
Audit Street Names
******************************
{'Mistyped street names': 8, 'Problem chars in street name': 9}
Estimated time:  0h 59min 15sec 378mls
```


###Audit Postcodes

In Prague postcodes have 5 digits and start from 1, second digit defines district of the city. 
For example address with postcode 12000 is in the city district "Prague 2". However there
 are some non-Prague postcodes, which correspond to villages close to the city.

Examples of invalid postcodes
 ```sh
 CZ - 130 00
 12000 Praha 7
 1051
 ```

Postcode validity is checked using the following simple regex expression:
```python
patt = r'^[1-9][0-9]{4}$' 
```

```sh
Audit report for the whole data set:
Audit Postcodes
******************************
{'Wrong type for post code': 7}
```

## Data Exploration

In this section data is explored with the help of SQL queries. All SQL queries are stored in separate .sql files in /sql/scripts. Queries are run with Python DB Api, results are stored in corresponding csv files in /sql/query_results.

###Find Vegetarian Restaurants

I like vegetarian restaurants and I would like to know which restaurants are the closest to my house location. In order to get this information I need a function which calculates distance between two points, defined by pairs of latitudes and longitudes. SQLite does not have a stored function/stored procedure language, as an alternative python DB API can be used.

Python package sqlite3 provides function 'create_function', which creates a user-defined function that can later be used from within SQL statements. 

```python
	...
	conn = sqlite3.connect(dbfilepath)
	conn.create_function("distance", 4, hvrs_dist)
	...
```

Function hvrs_dist uses external python package haversine and is defined as follows:

```python
from haversine import haversine

def hvrs_dist(lat1, lon1, lat2, lon2):
	return haversine((lat1, lon1), (lat2, lon2))
```

The following SQL query template can be used to selects a fixed number(LIMIT_THRSH) of vegetarian restaurants, which are the closest to specified location (TRG_LAT, TRG_LON):

```sql
SELECT N1.id,
       N1.value AS rest_name,
       N2.value AS addr_street,
       N3.value AS addr_hsnumber,
       N4.value AS rest_phone,
       distance(B.lat, B.lon, TRG_LAT, TRG_LON) AS dist
FROM nodes_tags N1
INNER JOIN
  (SELECT n.id,
          n.lat,
          n.lon
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   WHERE nt.key = "cuisine"
     AND (nt.value LIKE "%vegetarian%"
          OR nt.value LIKE "%vegan_food%"
          OR nt.value LIKE "%vegan%") ) B ON (N1.id = B.id)
LEFT JOIN nodes_tags N2 ON (N1.id = N2.id
                            AND N2.key="street")
LEFT JOIN nodes_tags N3 ON (N1.id = N3.id
                            AND N3.key="housenumber")
LEFT JOIN nodes_tags N4 ON (N1.id = N4.id
                            AND N4.key="phone")
WHERE N1.key = "name"
ORDER BY dist LIMIT LIMIT_THRSH
```
Example of 10 vegetarian restaurants closest to the metro station Namesti Miru (LIMIT_THRSH=10, TRG_LAT=50.075104, TRG_LON=14.437783):

|id|restaurant|street|hsnumber|phone|dist (km)|
|--------|--------|-----|-------|-----------|-----------|
|3725294145|Loving Hut|Londýnská|35|420 222 515 006|0.348618262955|
|3722700025|Etnosvět|Legerova|40|+420 226203880|0.554828543945|
|3725310177|Loving Hut|Jungmannova|18|None|1.26504911848|
|296542635|Salé|Orebitská|194/14|None|1.37304931465|
|3188225062|Gouranga|None|None|None|1.4832202835|
|3615466837|Loving Hut|Neklanova|30|None|1.53952159764|
|3715489329|Zdravé žití u tří růží|Soukenická|1190/21|+420 222 318 726|1.87560233767|
|3346737424|Dharmasala|Peckova|None|None|1.90294241462|
|941177533|Mlsná kavka|None|None|+420777913054|1.90354046063|
|4009231866|Veggie Garden|None|None|None|1.92520166077|

###Find Playgrounds

All parents who have small kids would like to know where the closest playgrounds are located. The following SQL query template can help with that. It selects fixed number (LIMIT_THRSH) of playgrounds closest to specified location (TRG_LAT, TRG_LON):

```sql
SELECT A.id,
       B.value AS playground,
       A.lt,
       A.ln,
       distance(A.lt, A.ln, TRG_LAT, TRG_LON) AS dist
FROM
  (SELECT wt.id,
          avg(n.lat) AS lt,
                        avg(n.lon) AS ln
   FROM ways w
   INNER JOIN
     (SELECT wn.id,
             n.lat,
             n.lon
      FROM ways_nodes wn
      INNER JOIN nodes n ON (wn.node_id = n.id) ) AS n ON (w.id = n.id)
   INNER JOIN ways_tags wt ON (w.id = wt.id
                               AND n.id=wt.id)
   WHERE wt.key="leisure"
     AND wt.value="playground"
   GROUP BY wt.id) A
LEFT JOIN ways_tags B ON (A.id = B.id
                          AND B.key="name")
ORDER BY dist LIMIT LIMIT_THRSH
```
Example of 5 playgrounds closest to the metro station Namesti Miru (LIMIT_THRSH=5, TRG_LAT=50.075104, TRG_LON=14.437783):

|id |playground|lat|lon|dist(km)|
|----------|--------------|----------|------------|-------------|
|115511512|None|50.0725020625|14.44522195|0.604600014152|
|28254035|Horní hřiště|50.0706216333|14.4444128583|0.687232605664|
|284577445|U Vodárny|50.07587525|14.448337225|0.758041834989|
|278208918|U Draka|50.0809563789|14.4434010789|0.764330752018|
|337383525|None|50.0825131364|14.443435|0.917280558432|


###District Statistics

Here are some statistics for different Prague districs. District number is extracted from the postcode.

```sql
SELECT PC.code,
       R.count_rest,
       P.count_bars,
       S.count_supermarkets,
       T.count_tourist
FROM
  (SELECT DISTINCT substr(value, 1, 2) AS code
   FROM nodes_tags
   WHERE KEY = "postcode"
     AND substr(value,1,1)="1" ) PC
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_rest
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "amenity"
     AND nt.value = "restaurant"
     AND nt1.KEY="postcode"
   GROUP BY code ) R ON (PC.code = R.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_bars
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "amenity"
     AND (nt.value = "pub"
          OR nt.value="bar")
     AND nt1.KEY="postcode"
   GROUP BY code ) P ON (PC.code = P.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_supermarkets
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "shop"
     AND nt.value = "supermarket"
     AND nt1.KEY="postcode"
   GROUP BY code ) S ON (PC.code = S.code)
LEFT JOIN
  (SELECT substr(nt1.value,1,2) AS code,
                                   count(*) AS count_tourist
   FROM nodes n
   INNER JOIN nodes_tags nt ON (n.id = nt.id)
   INNER JOIN nodes_tags nt1 ON (n.id = nt1.id)
   WHERE nt.KEY = "tourism"
     AND nt1.KEY="postcode"
   GROUP BY code ) T ON (PC.code = T.code)
   
  ```
Query result:

|District|# Restaurants|# Bars|# Supermarkets|# Tourist Objects|
|--------|-------------|------|--------------|-----------------|
|10|60|13|4|10|
|11|327|56|12|171|
|12|122|37|4|75|
|13|15|6|1|6|
|14|66|13|6|9|
|15|88|29|3|8|
|16|52|10|8|13|
|17|26|8|5|5|
|18|21|11|2|5|
|19|19|9|1|2|

We can see that central districts like Prague 1(11) and Prague 2(12) have much more tourist objects, number of restaurants and bars is also higher than in other districts.

##Conclusion

The OpenStreetMap data provides a lot of useful information which can be incorporated into different projects and applications. However since this data is open for different contributors, it is prone to errors and requires careful cleaning.
In this project I have performed detailed audit of address information and  implemented a few cleaning strategies.




