from db import get_db_connection
import requests

def getTournamentList():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT t_tourneyid, t_name, t_format, t_maxplayers, COUNT(pl_playerid)
                    FROM \"Tournament\"  LEFT JOIN \"Player\" on pl_tourneyid = t_tourneyid GROUP BY t_tourneyid ORDER BY t_name Asc;""")
    tournamentresults = cursor.fetchall()

    cursor.close()
    conn.close()
    return tournamentresults

def selectTournament(t_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM \"Tournament\" WHERE t_tourneyID = %s;", (t_tourneyid,))
    selectedTournament = cursor.fetchone()

    cursor.close()
    conn.close()
    return selectedTournament

def newTournament(name, tformat, playercount):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO \"Tournament\"(t_name, t_format, t_maxplayers) VALUES (%s, %s, %s);", (name, tformat, playercount,))
    conn.commit()

    cursor.close()
    conn.close()
    return

def updateTournament(t_tourneyid, name, tformat, playercount):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE \"Tournament\" SET t_name = %s, t_format = %s, t_maxplayers = %s WHERE t_tourneyid = %s;", (name, tformat, playercount, t_tourneyid))

    conn.commit()
    cursor.close()
    conn.close()
    return

def deleteTournament(t_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM \"Tournament\" WHERE t_tourneyid = %s;", (t_tourneyid,))
    conn.commit()

    cursor.close()
    conn.close()
    return