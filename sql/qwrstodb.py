import sqlite3
from haversine import haversine
import select_qwrs as qwrs
import pprint as pp

def hvrs_dist(lat1, lon1, lat2, lon2):
	return haversine((lat1, lon1), (lat2, lon2))


def run_queries(dbfilepath, queries, names, trg_location, top):
	""" Creates sqlite function for haversine distance calculation """

	conn = sqlite3.connect(dbfilepath)
	conn.create_function("distance", 4, hvrs_dist)
	cur = conn.cursor()
	
	for i, q in enumerate(queries):
		cur.execute(q.replace("LIMIT_THRSH", str(top)).replace("TRG_LAT", trg_location[0]).replace("TRG_LON", trg_location[1]) )
		print names[i]
		print "************************"	
		results = cur.fetchall() 
		for result in results:
			print u"{}".format(result)

		print "************************"	

	

if __name__ == "__main__":
	dbfilepath = "..\\data\\prgstrmap.db"
	test_dbfilepath = "..\\data\\test_prgstrmap.db"

	#Define target location
	nam_miru = ("50.075104", "14.437783")  #Location of metro station Namesti Miru
	#mustek = ("50.083031", "14.422137") #Location of metro station Mustek
	
	queries = [qwrs.closest_veg_restaurants, qwrs.close_playgrounds]
	names = ["Vegeterian Restaurants", "Playgrounds"]
	run_queries(dbfilepath, queries, names, nam_miru, 10)