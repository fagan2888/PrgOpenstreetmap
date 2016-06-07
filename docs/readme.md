### Prague OpenStreetMap Project

### Address Audit

To perform audit of address information  run the following command in a terminal (from the project directory):

```
python -m openstrmap.auditaddr

```
After running this command you will get audit report, more detailed information about detected data problems can be found in corresponding log files in \openstrmap\log\.


### Data Processing
To run data processing module run the following command in a terminal (from the project directory) 
```
python -m openstrmap.data

```

This python module parse OSM input file, fix some address problems and prepare csv files for further import into database.
Csv files are stored in openstrmap\ folder, details of all performed corrections are stored in log file in \openstrmap\log\fixaddr.log. 

One of corrections is related to mistyped street names (see details in project report), a list of mistyped street names is formed from audit log file openstrmap\log\audit_strnames.log. This file can be manually checked and edited in before running data processing and correction. 
    

###Create and Explore Database

To create SQLite database with defined scheme , run the following command in a terminal (from the project directory):
```
python -m sql.loadtodb

```

This module creates db file and runs SQL script from sql\scripts\createdb.sql

To import csv files into database repeat the following command for each file (run in SQLite terminal):

```
.separator ","
.import csv_file_path db_table

```

To run SQL queries, run the following command in a terminal (from the project directory):
```
python -m sql.qwrstodb

```
SQL scripts are stored in the folder \slq\scripts and query results are written in csv files in \sql\query_results. Names of csv files correspond to the names of sql scripts.







