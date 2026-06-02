from db import get_db_connection
import requests

def getSetList(s_matchid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT s_setid, s_matchid, s_player1id, p1.pl_name, s_player2id, p2.pl_name, s_winid, s_link, s_date, s_points, s_setnum 
    FROM \"Sets\" JOIN \"Player\" p1 ON p1.pl_playerid = s_player1id JOIN \"Player\" p2 ON p2.pl_playerid = s_player2id WHERE s_matchID = %s;
    """, (s_matchid,))
    match_results = cursor.fetchall()

    cursor.execute("""
            SELECT s_matchid, COUNT(CASE WHEN s_player1id = s_winid THEN 1 END), COUNT(CASE WHEN s_player2id = s_winid THEN 1 END)
            FROM \"Sets\" WHERE s_matchID = %s GROUP BY s_matchid; """,(s_matchid,))
    wincount = cursor.fetchone()

    cursor.close()
    conn.close()
    return match_results, wincount

def newSet(s_matchid, s_player1id, s_player2id, s_winid, s_link, s_date, s_points, s_setnum):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO \"Sets\"(s_matchid, s_player1id, s_player2id, s_winid, s_link, s_date, s_points, s_setnum) VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING s_setID;""", (s_matchid, s_player1id, s_player2id, s_winid, s_link, s_date, s_points, s_setnum))
    setid = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()
    return setid

def registerPokemonInSet(s_setid, ps_roster, ps_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    for pokemon in ps_roster:
        cursor.execute("""INSERT INTO \"PokemonSet\"(ps_setid, ps_pokeid, ps_playerid, ps_k, ps_d, ps_streak, ps_tera)
                        VALUES(%s, %s, %s, %s, %s, %s, %s); """, (s_setid, pokemon["id"], ps_playerid,
                                                                   pokemon["kills"], pokemon["deaths"],
                                                                   pokemon["streak"], pokemon["tera"]))
        conn.commit()

    cursor.close()
    conn.close()
    return
