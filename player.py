from db import get_db_connection
import requests

def getPlayerList(pl_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Player WHERE pl_tourneyID = %s ORDER BY pl_name ASC;", (pl_tourneyid,))
    player_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return  player_results

def selectPlayer(pl_tourneyid, pl_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Player WHERE (pl_tourneyID = %s and pl_playerid = %s);", (pl_tourneyid,pl_playerid,))
    selectedplayer = cursor.fetchone()
    playername = selectedplayer[1]

    cursor.close()
    conn.close()
    return  selectedplayer, playername

def newPlayer(pl_tourneyid, name, contraint, url):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Player(pl_name, pl_type, pl_tourneyid, pl_pokepaste) VALUES (%s, %s, %s, %s);", (name, contraint, pl_tourneyid,url,))
    conn.commit()

    cursor.close()
    conn.close()
    return

def editPlayer(pl_tourneyid, pl_playerid, name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE Player SET pl_name = %s WHERE (pl_tourneyid = %s AND pl_playerid = %s);",
                   (name, pl_tourneyid, pl_playerid))
    conn.commit()
    cursor.close()
    conn.close()
    return

def deletePlayer(pl_tourneyid, pl_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Player WHERE (pl_tourneyid = %s AND pl_playerid = %s);", (pl_tourneyid, pl_playerid,))
    conn.commit()

    cursor.close()
    conn.close()

    return