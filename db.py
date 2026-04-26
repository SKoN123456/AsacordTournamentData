import psycopg2

config = {
    'host': 'localhost',
    'database': 'pokemontournamentdata',
    'user': 'postgres',
    'password': 'newpassword',
    'port': 5432
}

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(**config)
    return conn