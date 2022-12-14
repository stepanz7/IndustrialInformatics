import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# conn = sqlite3.connect(':memory:', check_same_thread= False)
conn = sqlite3.connect('database_testing.db', check_same_thread=False)
conn.row_factory = dict_factory
database_name = "database"

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS Event (
             messageID INTEGER PRIMARY KEY AUTOINCREMENT,
             robotID text,
             state text,
             timeStamp integer
             );""")

#CREATE
def insert_robot_message(id,state,timestamp):
    with conn:
        c.execute("INSERT INTO Event VALUES (:id,:robotID,:state,:timeStamp)", {'id': None, 'robotID': id, 'state': state, 'timeStamp': timestamp })

#READ
def get_all_messages():
    #c.execute("SELECT * FROM robot WHERE brand=:brand", {'brand': brand})
    sqlSt="SELECT * FROM Event"
    c.execute(sqlSt)
    return c.fetchall()

#READ
def get_messages_by_robID(robID):
    #c.execute("SELECT * FROM robot_messages WHERE robotID=:robotID"
    sqlSt=f"SELECT * FROM Event WHERE robotID = {robID}"
    c.execute(sqlSt)
    return c.fetchall()

def  get_messages_time_window(start, end):
    #c.execute("SELECT * FROM robot_messages WHERE start <= timestamp <= end")
    sqlSt=f"SELECT * FROM Event WHERE {start} <= timeStamp <= {end}"
    c.execute(sqlSt)
    return c.fetchall()

def get_latest_message_by_robotID(id):
    sqlSt = f"SELECT * from Event WHERE robotID == '{id}' ORDER BY timeStamp DESC LIMIT 1"
    c.execute(sqlSt)
    return c.fetchall()

def get_all_messages_by_robotID_and_time(id, start, end):
    sqlSt = f"SELECT * from Event WHERE robotID == '{id}' AND timeStamp > {start} AND timeStamp < {end}"
    c.execute(sqlSt)
    return c.fetchall()



