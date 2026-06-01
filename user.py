from db import get_db_connection
import requests

def newUser(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO \"User\" (u_username, u_password) VALUES (%s, crypt(%s, gen_salt('md5')))", (username, password))

    cursor.close()
    conn.close()
    return