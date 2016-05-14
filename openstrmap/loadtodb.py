import sqlite3

dbfilepath = "..\\data\\prgstrmap.db"
test_dbfilepath = "..\\data\\test_prgstrmap.db"

crtdb_sql = ""
crtdb_sql_path = "..\\sql\\createdb.sql"

with open(crtdb_sql_path) as f:
	crtdb_sql = f.read()

conn = sqlite3.connect(test_dbfilepath)
curs = conn.cursor()
curs.executescript(crtdb_sql)
conn.commit()