from db import get_db_connection
import requests

def getTournamentList():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Tournament ORDER BY t_name Asc;")
    tournamentresults = cursor.fetchall()

    cursor.close()
    conn.close()

    return tournamentresults

def selectTournament(t_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Tournament WHERE t_tourneyID = %s;", (t_tourneyid,))
    selectedTournament = cursor.fetchone()

    cursor.close()
    conn.close()

    return selectedTournament

def newTournament(name, tformat):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO TOURNAMENT(t_name, t_format) VALUES (%s, %s);", (name, tformat))
    conn.commit()

    cursor.close()
    conn.close()

    return

def updateTournament(t_tourneyid, name, tformat):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE Tournament SET t_name = %s, t_format = %s WHERE t_tourneyid = %s;", (name, tformat, t_tourneyid))

    conn.commit()
    cursor.close()
    conn.close()

    return

def deleteTournament(t_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Tournament WHERE t_tourneyid = %s;", (t_tourneyid,))
    conn.commit()

    cursor.close()
    conn.close()

    return