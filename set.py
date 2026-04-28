from db import get_db_connection
import requests

def getSetList(s_matchid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Sets WHERE s_matchID = %s;", (s_matchid,))
    match_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return match_results