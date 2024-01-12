from dotenv import dotenv_values
from sqlalchemy import create_engine,text
import urllib
import pandas as pd
import pyodbc
import os

config = dotenv_values(".env")
server = os.getenv('Server')
database = os.getenv('Database')
user = os.getenv('User')
password = os.getenv('Pass')

def read_db_conn_details() -> dict:
    """Output of this should be passed to the create_engine function of sqlalchemy"""

    params = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={user};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
    
    return params

def df_from_db(query: str) -> pd.DataFrame:
    params = read_db_conn_details()
    conn_str = "mssql+pyodbc:///?odbc_connect=" + params
    engine = create_engine(conn_str)
    df = pd.read_sql_query(text(query), con=engine.connect())
    return df

def upload_data(data: list, table_name: str, username: str):

    # Establish a connection to the database
    cnxn = pyodbc.connect(
        f"DRIVER=ODBC Driver 17 for SQL Server;"
        f"SERVER={config['Server']};"
        f"DATABASE={config['Database']};"
        f"UID={config['User']};"
        f"PWD={config['Pass']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30"
    )
    

    # Create a cursor object to interact with the database
    cursor = cnxn.cursor()
    schema = 'BMT'

    for record in data:
        # Delete records if the current input data exists in the table
        delete_query = f'''
        DELETE FROM {schema}.{table_name}
        WHERE supplier = ? AND focus = ? AND num_search = ? AND username = ?
        '''
        # Upload data to the table
        insert_query = f'''
            INSERT INTO {schema}.{table_name} (supplier, focus, num_search, username)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(delete_query, record['supplier'], record['focus'], record['num_search'], username)
        cursor.execute(insert_query, record['supplier'], record['focus'], record['num_search'], username)

    # Commit the changes to the database
    cnxn.commit()
    
    # Close the cursor and connection
    cursor.close()
    cnxn.close()



