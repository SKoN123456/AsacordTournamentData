import psycopg2

config = {
    'host': 'aws-1-us-west-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.hjrvoawkstxtcmchmevc',
    'password': 'HiAvailing976'
}

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(**config)
    return conn