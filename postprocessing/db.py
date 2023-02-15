import sys 
import csv
import sqlite3


DB_FILE = "./data.db"
HOSTNAME_MAP = {
    'ip-10-0-5-216'  : "graviton3",
    'ip-10-0-128-152': "icelake",
    'ip-10-0-129-120': "graviton2",
    'ip-10-0-5-250'  : "zen3",
    'ip-10-0-7-30'   : "skylake",
    'ip-10-0-6-160'  : "haswell",
    'archlinux'      : "zen2",
}
USER_MAP = {
    'upstream': 'upstream',
    'hack'    : 'hack',
    'ubuntu'  : 'hack',
}


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
            mapped_hostname = HOSTNAME_MAP.get(row["Hostname"], row["Hostname"])
            mapped_user = USER_MAP.get(row["User"])
            cur.execute(
                "INSERT INTO benchmarks VALUES (?, ?, ?, ?, ?, ?)", (
                mapped_hostname, mapped_user, row["Script"],
                row["Trial"], row["Threads"], row["Speed"])
            )

    con.commit()
    con.close()

def delete_data(file):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
        for row in reader:
            mapped_hostname = HOSTNAME_MAP.get(row["Hostname"], row["Hostname"])
            mapped_user = USER_MAP.get(row["User"])
            cur.execute(
                "DELETE FROM benchmarks "
                "WHERE hostname=? AND user=? AND script=? AND trial=? AND threads=? AND speed=?",
                (
                    mapped_hostname, mapped_user, row["Script"],
                    row["Trial"], row["Threads"], row["Speed"]
                )
            )

    con.commit()
    con.close()

if sys.argv[1] == "init":
    init()
elif sys.argv[1] == "import":
    import_data(sys.argv[2])
elif sys.argv[1] == "delete":
    delete_data(sys.argv[2])
