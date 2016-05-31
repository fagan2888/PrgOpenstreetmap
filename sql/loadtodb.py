import sqlite3
from haversine import haversine

def loadtodb(dbfilepath, crtdb_sql_path):
	""" Runs sql script to create basic tables """
	
	crtdb_sql = ""
	with open(crtdb_sql_path) as f:
		crtdb_sql = f.read()

	conn = sqlite3.connect(dbfilepath)
	curs = conn.cursor()
	curs.executescript(crtdb_sql)
	conn.commit()


if __name__ == "__main__":
	dbfilepath = "..\\data\\prgstrmap.db"
	test_dbfilepath = "..\\data\\test_prgstrmap.db"
	crtdb_sql_path = "..\\sql\\createdb.sql"

	loadtodb(dbfilepath, crtdb_sql_path)

	
