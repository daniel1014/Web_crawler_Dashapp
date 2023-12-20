from dotenv import dotenv_values
from sqlalchemy import create_engine
import urllib
import re
from pathlib import Path
import pickle
import pandas as pd
import os

def read_db_conn_details() -> dict:
    """Output of this should be passed to df_from_db "db_conn_details" arg"""
    config = dotenv_values(".env")
    return {
        "Server": config["Server"],
        "Database": config["Database"],
        "User": config["User"],
        "Pass": config["Pass"],
    }


def df_from_db(query: str, db_conn_details: dict) -> pd.DataFrame:
    params = urllib.parse.quote_plus(
        "Driver={SQL Server};"
        + f"Server=tcp:{db_conn_details['Server']},1433;"
        + f"Database={db_conn_details['Database']};"
        + f"Uid={db_conn_details['User']};"
        + f"Pwd={db_conn_details['Pass']};"
    )
    conn_str = "mssql+pyodbc:///?odbc_connect=" + params
    engine = create_engine(conn_str)
    df = pd.read_sql(query, engine)
    return df

def store_results(result: list):
    db_conn_details = read_db_conn_details()
    params = urllib.parse.quote_plus(f"DRIVER={{SQL Server}};SERVER={db_conn_details['Server']};DATABASE={db_conn_details['Database']};UID={db_conn_details['User Id']};PWD={db_conn_details['Password']}")
    conn_str = f"mssql+pyodbc:///?odbc_connect={params}"
    engine = create_engine(conn_str)
    df = pd.DataFrame(result)
    df.to_sql(name='news_output', con=engine, schema='BMT', if_exists='append', index=False)

# db_conn_details = read_db_conn_details()
# query = "SELECT aecom_code2 FROM BMT.Asset"
# df = df_from_db(query, db_conn_details)
# print(df)
    
# def get_all_results(supplier_input, focus_input):
#     if supplier_input != "" and focus_input != "":
#         query = f"SELECT * FROM dbo.all_results WHERE supplier = '{supplier_input}' AND focus = '{focus_input}'"
