DROP TABLE IF EXISTS Tournament CASCADE;
DROP TABLE IF EXISTS Player CASCADE;
DROP TABLE IF EXISTS Pokemon CASCADE;
DROP TABLE IF EXISTS Matches CASCADE;

CREATE TABLE Tournament(
	t_tourneyID SERIAL PRIMARY KEY,
	t_name VARCHAR(50),
	t_format VARCHAR(25)
);

CREATE TABLE Player(
	pl_playerID SERIAL PRIMARY KEY,
	pl_name VARCHAR(20),
	pl_type VARCHAR(20),
	pl_tourneyID INT NOT NULL,
	pl_total_sets INT DEFAULT 0,
	pl_match_wins INT DEFAULT 0,
	pl_matchlosses INT DEFAULT 0,
	pl_set_wins INT DEFAULT 0,
	pl_totalk INT DEFAULT 0,
	pl_totald INT DEFAULT 0,
	pl_avgr FLOAT DEFAULT 0.00,
	pl_totalbrought INT DEFAULT 0,
	FOREIGN KEY (pl_tourneyID) REFERENCES Tournament(t_tourneyID),
	UNIQUE (pl_name, pl_tourneyid)
);

CREATE TABLE Pokemon(
	po_pokeID SERIAL PRIMARY KEY,
	po_tourneyID INT NOT NULL,
	po_playerName VARCHAR(20),
	po_name VARCHAR(50),
	po_type1 VARCHAR(20),
	po_type2 VARCHAR(20),
	po_tier VARCHAR(5),
	po_isTeraCaptain BOOLEAN DEFAULT FALSE,
	po_k INT DEFAULT 0,
	po_d INT DEFAULT 0,
	po_numBrought INT DEFAULT 0,
	po_winstreak INT DEFAULT 0,
	po_R FLOAT DEFAULT 0.00,
	po_percentBrought FLOAT DEFAULT 0.00,
	po_speed INT NOT NULL,
	po_modSpeed INT NOT NULL,
	FOREIGN KEY (po_playername, po_tourneyID) REFERENCES Player(pl_name,pl_tourneyID)
);

CREATE TABLE Matches(
	m_matchid SERIAL PRIMARY KEY,
	m_tourneyid INT NOT NULL,
	m_player1id INT NOT NULL, 
	m_player2id INT NOT NULL CHECK (m_player1id <> m_player2id),
	m_name VARCHAR(50),
	FOREIGN KEY (m_tourneyID) REFERENCES Tournament(t_tourneyID),
	FOREIGN KEY (m_player1id) REFERENCES Player(pl_playerID),
	FOREIGN KEY (m_player2id) REFERENCES Player(pl_playerID)
);

CREATE TABLE Sets(
	s_setID SERIAL PRIMARY KEY,
	s_matchid INT NOT NULL,
	s_player1ID INT NOT NULL,
	s_player2ID INT NOT NULL,
	s_winID INT, 
	s_link VARCHAR(200),
	s_date DATE DEFAULT CURRENT_DATE,
	s_points INT DEFAULT 0,
	s_setnum INT DEFAULT 0,
	FOREIGN KEY (s_matchid) REFERENCES Matches(m_matchid),
	FOREIGN KEY (s_player1ID) REFERENCES Player(pl_playerID),
	FOREIGN KEY (s_player2ID) REFERENCES Player(pl_playerID),
	FOREIGN KEY (s_winID) REFERENCES Player(pl_playerID)
);

CREATE TABLE PokemonSet(
	ps_setID INT NOT NULL,
	ps_pokeID INT NOT NULL,
	ps_playerID INT NOT NULLm
	ps_k INT DEFAULT 0,
	ps_d INT DEFAULT 0,
	ps_r FLOAT DEFAULT 0.00,
	ps_streak INT DEFAULT 0,
	PRIMARY KEY (ps_setid, ps_pokeid, ps_playerid),
	FOREIGN KEY (ps_matchID) REFERENCES Sets(s_setID),
	FOREIGN KEY (ps_pokeID) REFERENCES Pokemon(po_pokeID),
	FOREIGN KEY (ps_playerID) REFERENCES Player(pl_playerID)
);
