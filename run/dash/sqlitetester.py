
import pandas as pd
import sqlite3

conn = sqlite3.connect("shoebox.db")
df = pd.read_sql_query("select * from sneakers limit 20;", conn)
print(df)

conn.close()