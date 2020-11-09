
import os
import sqlite3
from sqlite3 import Error

def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        return conn

def create_table(conn, query):

    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)
