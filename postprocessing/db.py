import sys 
import csv
import sqlite3


DB_FILE = "./data.db"


def init():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute('''
                   CREATE TABLE benchmarks
                   (
                       hostname TEXT,
                       user TEXT,
                       script TEXT,
                       trial INTEGER,
                       threads INTEGER,
                       speed REAL
                   )
                   ''')
    con.commit()
    con.close()

def import_data(file):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
        for row in reader:
            cur.execute(
                "INSERT INTO benchmarks VALUES (?, ?, ?, ?, ?, ?)", (
                row["Hostname"], row["User"], row["Script"],
                row["Trial"], row["Threads"], row["Speed"])
            )

    con.commit()
    con.close()

if sys.argv[1] == "init":
    init()
elif sys.argv[1] == "import":
    import_data(sys.argv[2])
