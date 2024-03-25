import os
from dotenv import load_dotenv

load_dotenv()

def get_postgre_database(database: str):
    load_dotenv()

    DB_PASSWORD = os.environ["SUPABASE_PASSWORD"]
    DB_DBUSER = os.environ["SUPABASE_DBUSER"]
    DB_HOST = os.environ["SUPABASE_HOST"]
    DB_PORT = os.environ["SUPABASE_PORT"]
    DB_DATABASE = database
    DB_CONN_STRING = (
        # postgresql+psycopg2:
        f"postgresql://{DB_DBUSER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    return DB_CONN_STRING