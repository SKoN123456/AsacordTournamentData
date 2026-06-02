from db import get_db_connection
import requests

def newUser(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO \"User\" (u_username, u_password) VALUES (%s, crypt(%s, gen_salt('md5'))) 
                    RETURNING u_userid, u_username, u_create, u_update, u_delete""", (username, password))
    user = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()
    return user

def selectUser(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT (u_password = crypt(%s, u_password)) FROM \"User\" WHERE u_username = %s ;", (password, username))
    validation = cursor.fetchone()

    cursor.execute("SELECT u_userid, u_username, u_create, u_update, u_delete FROM \"User\" WHERE u_username = %s ;", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return validation, user