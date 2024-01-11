from dotenv import dotenv_values
from sqlalchemy import create_engine,text
import urllib
import pandas as pd
import pyodbc

def read_db_conn_details() -> dict:
    """Output of this should be passed to the create_engine function of sqlalchemy"""
    config = dotenv_values(".env")
    params = urllib.parse.quote_plus(
        "Driver={SQL Server};"
        + f"Server=tcp:{config['Server']},1433;"
        + f"Database={config['Database']};"
        + f"Uid={config['User']};"
        + f"Pwd={config['Pass']};"
    )
    return params

def df_from_db(query: str) -> pd.DataFrame:
    params = read_db_conn_details()
    conn_str = "mssql+pyodbc:///?odbc_connect=" + params
    engine = create_engine(conn_str)
    try:
        df = pd.read_sql_query(text(query), con=engine.connect())
        return df
    except Exception as e:
        print(f"Error reading data from the database: {str(e)}")
        return None

def upload_data(data: list, table_name: str, username: str):
    db_conn_details = dotenv_values(".env")

    # Establish a connection to the database
    cnxn = pyodbc.connect(
        f"DRIVER=ODBC Driver 17 for SQL Server;"
        f"SERVER={db_conn_details['Server']};"
        f"DATABASE={db_conn_details['Database']};"
        f"UID={db_conn_details['User']};"
        f"PWD={db_conn_details['Pass']}"
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



