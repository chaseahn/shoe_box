import sqlite3

def run(dbname='shoebox.db'):

    CON = sqlite3.connect(dbname)
    CUR = CON.cursor()

    CUR.execute("""DROP TABLE IF EXISTS user;""")
    # create accounts table
    CUR.execute("""CREATE TABLE user(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR,
        password VARCHAR,
        age INTEGER,
        gender VARCHAR,
        CONSTRAINT unique_username UNIQUE(username)
    );""")

    CUR.execute("""DROP TABLE IF EXISTS request_shoe;""")
    # create positions table
    CUR.execute("""CREATE TABLE request_shoe(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        time INTEGER,
        requests INTEGER,
        user_pk INTEGER,
        FOREIGN KEY(user_pk) REFERENCES user(pk)
    );""")

    CON.commit()
    CUR.close()
    CON.close()

if __name__ == '__main__':
    run()