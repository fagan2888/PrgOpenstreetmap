import sqlite3
from haversine import haversine
from time import time

#import sys, os
#sys.path.insert(0, os.path.abspath('..'))
import openstrmap.helper as hlp

def hvrs_dist(lat1, lon1, lat2, lon2):
	return haversine((lat1, lon1), (lat2, lon2))

def run_queries(dbfilepath, queries, outfiles):
	""" Creates sqlite function for haversine distance calculation """

	conn = sqlite3.connect(dbfilepath)
	conn.create_function("distance", 4, hvrs_dist)
	cur = conn.cursor()
	
	for i, q in enumerate(queries):
		outfile = outfiles[i]
		print "Calculating {}...".format(outfile.split(".")[0])
		start = time()
		cur.execute(q)
		query_result = cur.fetchall() 
		print "Time Elapsed: {} mls".format(hlp.pretty_time(time()-start))
		print "*************************************"
		columns = [description[0] for description in cur.description]
		with open(outfile, "w") as f:
			f.write(format_row(columns))
			for row in query_result:
				f.write(format_row(row))
		


def format_row(row, delimiter=","):
	n = len(row)
	out = ('{}'+delimiter)*(n-1) + "{}\n"

	new_row = []
	for r in row:
		try:
			new_r = str(r)
		except UnicodeEncodeError:
			new_r = r.encode("utf-8")
		new_row.append (new_r)

	return out.format(*new_row)
	

if __name__ == "__main__":
	dbfilepath = "data\\prgstrmap.db"
	test_dbfilepath = "data\\test_prgstrmap.db"

	#TO DO: Organize parameter setting in a proper way

	#Define target location
	nam_miru = ("50.075104", "14.437783")  #Location of metro station Namesti Miru
	#mustek = ("50.083031", "14.422137") #Location of metro station Mustek
	
	top = 10
	trg_location = nam_miru
	
	qfiles = ['sql\\scripts\\close_veg_restaurants.sql', 
			  'sql\\scripts\\close_playgrounds.sql', 
			  'sql\\scripts\\district_stat.sql'
			 ]

	queries = []
	for i, qfile in enumerate(qfiles):
		with open(qfile) as f:
			queries.append(f.read())

	queries[0] = queries[0].replace("LIMIT_THRSH", str(top)).replace("TRG_LAT", trg_location[0]).replace("TRG_LON", trg_location[1])
	queries[1] = queries[1].replace("LIMIT_THRSH", str(top)).replace("TRG_LAT", trg_location[0]).replace("TRG_LON", trg_location[1])

	
	outfiles = ["sql\\query_results\\close_veg_restaurants.csv", "sql\\query_results\\close_playgrounds.csv", "sql\\query_results\\district_stat.csv"]
	map(hlp.create_path, outfiles) #Create path if needed

	run_queries(dbfilepath, queries, outfiles)	