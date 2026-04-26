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
	m_matchID SERIAL PRIMARY KEY,
	m_tourneyID INT NOT NULL,
	m_winID INT NOT NULL,
	m_lostID INT NOT NULL CHECK (m_winID <> m_lostID),
	m_link VARCHAR(200),
	m_date DATE DEFAULT CURRENT_DATE,
	FOREIGN KEY (m_tourneyID) REFERENCES Tournament(t_tourneyID),
	FOREIGN KEY (m_winID) REFERENCES Player(pl_playerID),
	FOREIGN KEY (m_lostID) REFERENCES Player(pl_playerID)
);
