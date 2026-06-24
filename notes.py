from db import get_db_connection

def newNote(n_userid, n_pokeid, n_playerid, n_matchid, n_setid, n_content):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO \"Notes\"(n_userid, n_pokeid, n_playerid, n_matchid, n_setid, n_content) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """, (n_userid, n_pokeid, n_playerid, n_matchid, n_setid, n_content))
    conn.commit()

    cursor.close()
    conn.close()
    return

def getNotes(n_userid, n_pokeid, n_playerid, n_matchid, n_setid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM \"Notes\" WHERE (n_userid = %s AND n_pokeid = %s)
        """, (n_userid, n_pokeid))
    note_results = cursor.fetchall()
    print(note_results)

    cursor.close()
    conn.close()
    return note_results