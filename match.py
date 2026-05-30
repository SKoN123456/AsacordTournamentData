from db import get_db_connection
import requests

def getMatchList(m_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m_matchid, m_tourneyid, m_name, m_player1id, p1.pl_name, m_player2id, p2.pl_name,
        COUNT(CASE WHEN m_player1id = s_winid THEN 1 END), COUNT(CASE WHEN m_player2id = s_winid THEN 1 END)
        FROM \"Matches\" JOIN \"Player\" p1 ON p1.pl_playerid = m_player1id JOIN \"Player\" p2 ON p2.pl_playerid = m_player2id 
        LEFT JOIN \"Sets\" ON s_matchid = m_matchid WHERE m_tourneyID = %s
        GROUP BY m_matchid, m_tourneyid, m_name, m_player1id, p1.pl_name, m_player2id, p2.pl_name ORDER BY m_name ASC;
    """, (m_tourneyid,))
    match_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return match_results

def selectMatch(m_matchid, m_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT m_name, p1.pl_name, p2.pl_name, m_player1id, m_player2id FROM \"Matches\" JOIN \"Player\" p1 ON p1.pl_playerid = m_player1id 
            JOIN \"Player\" p2 ON p2.pl_playerid = m_player2id WHERE m_tourneyid = %s AND m_matchid = %s
            """, (m_tourneyid, m_matchid,))
    selectedMatch = cursor.fetchone()

    cursor.close()
    conn.close()
    return selectedMatch

def newMatch(m_tourneyid, name, player1id, player2id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO \"Matches\"(m_tourneyid, m_player1id, m_player2id, m_name) VALUES (%s, %s, %s, %s)", (m_tourneyid, player1id, player2id, name,))
    conn.commit()

    cursor.close()
    conn.close()
    return