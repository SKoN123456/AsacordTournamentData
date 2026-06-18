from db import get_db_connection
import requests

def getPlayerList(pl_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM \"Player\" WHERE pl_tourneyID = %s ORDER BY pl_name ASC;", (pl_tourneyid,))
    player_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return  player_results

def selectPlayer(pl_tourneyid, pl_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM \"Player\" WHERE (pl_tourneyID = %s and pl_playerid = %s);", (pl_tourneyid,pl_playerid,))
    selectedplayer = cursor.fetchone()

    cursor.execute("""SELECT s_setid, s_link, s_setnum, s_points, s_player1id, p1.pl_name, s_player2id, p2.pl_name, s_winid FROM \"Sets\" 
                    JOIN \"Matches\" ON m_matchid = s_matchid JOIN \"Player\" p1 ON p1.pl_playerid = s_player1id JOIN \"Player\" p2 ON p2.pl_playerid = s_player2id
                    WHERE (s_player1id =%s OR s_player2id = %s) ORDER BY CASE WHEN s_winid = %s THEN 0 ELSE 1 END,
                    CASE WHEN s_winid = %s THEN -s_points ELSE s_points END LIMIT 5;""", (pl_playerid,pl_playerid,pl_playerid,pl_playerid,))
    best_sets = cursor.fetchall()

    cursor.close()
    conn.close()
    return  selectedplayer, best_sets

def selectPlayerByName(pl_tourneyid, pl_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM \"Player\" WHERE (pl_tourneyID = %s and pl_name = %s);", (pl_tourneyid, pl_name,))
    selectedplayer = cursor.fetchone()
    playerID = selectedplayer[0]

    cursor.close()
    conn.close()
    return playerID

def newPlayer(pl_tourneyid, name, contraint, url):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO \"Player\"(pl_name, pl_type, pl_tourneyid, pl_pokepaste) VALUES (%s, %s, %s, %s) RETURNING pl_playerID;", (name, contraint, pl_tourneyid,url,))
    playerid = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()
    return playerid

def editPlayer(pl_tourneyid, pl_playerid, name, url):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE \"Player\" SET pl_name = %s, pl_pokepaste = %s WHERE (pl_tourneyid = %s AND pl_playerid = %s);",
                   (name, url, pl_tourneyid, pl_playerid))
    conn.commit()
    cursor.close()
    conn.close()
    return

def deletePlayer(pl_tourneyid, pl_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM \"Player\" WHERE (pl_tourneyid = %s AND pl_playerid = %s);", (pl_tourneyid, pl_playerid,))
    conn.commit()

    cursor.close()
    conn.close()

    return