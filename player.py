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

    cursor.execute("""SELECT pl_playerid, pl_name, pl_type, pl_pfp, COALESCE(s.total_sets, 0) AS total_sets, COALESCE(s.set_wins, 0) AS set_wins, COALESCE(SUM(ms.win), 0) AS match_wins, COALESCE(SUM(ms.loss), 0) AS match_losses, COALESCE(ps.total_k, 0) AS total_k, COALESCE(ps.total_d, 0) AS total_d, pl_pokepaste FROM "Player"
LEFT JOIN (SELECT ps_playerid, SUM(ps_k) AS total_k, SUM(ps_d) AS total_d FROM "PokemonSet" GROUP BY ps_playerid) ps ON ps_playerid = pl_playerid
LEFT JOIN (SELECT player_id, COUNT(DISTINCT s_setid) AS total_sets, COUNT(CASE WHEN player_id = s_winid THEN 1 END) AS set_wins
    FROM (SELECT s_player1id AS player_id, s_setid, s_winid FROM "Sets" UNION ALL SELECT s_player2id AS player_id, s_setid, s_winid FROM "Sets") x
    GROUP BY player_id) s ON s.player_id = pl_playerid
LEFT JOIN (SELECT player_id, p1sets, win1id, p2sets, win2id,
 CASE WHEN ((player_id = win1id AND p1sets > p2sets) OR (player_id = win2id AND p1sets < p2sets)) THEN 1 ELSE 0 END AS win,
 CASE WHEN ((player_id = win1id AND p1sets < p2sets) OR (player_id = win2id AND p1sets > p2sets)) THEN 1 ELSE 0 END AS loss
FROM (SELECT m_matchid, m_player1id, m_player2id, 
    COUNT(CASE WHEN m_player1id = s_winid THEN 1 END) as p1sets, m_player1id AS win1id, COUNT(CASE WHEN m_player2id = s_winid THEN 1 END) as p2sets, m_player2id AS win2id FROM "Matches" LEFT JOIN "Sets" ON s_matchid = m_matchid GROUP BY m_matchid, m_player1id, m_player2id) match_winners
    JOIN (SELECT s_matchid, s_player1id AS player_id FROM "Sets" UNION ALL SELECT s_matchid, s_player2id AS player_id FROM "Sets") players
    ON match_winners.m_matchid = players.s_matchid GROUP BY player_id, p1sets, win1id, p2sets, win2id) ms ON ms.player_id = pl_playerid 
    WHERE (pl_tourneyid = %s AND pl_playerid = %s) GROUP BY pl_playerid, pl_name, pl_type, pl_pfp, s.total_sets, s.set_wins, ps.total_k, ps.total_d;""", (pl_tourneyid,pl_playerid,))
    selectedplayer = cursor.fetchone()
    print(selectedplayer)

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