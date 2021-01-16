import pyodbc

import config

O2JAM_SQL_CONNECTION_STRING = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'.format(
    '{ODBC Driver 17 for SQL Server}',
    config.SQL_SERVER_IP,
    'O2JAM',
    config.SQL_ACCOUNT_ID,
    config.SQL_ACCOUNT_PASSWORD
)

O2JAMTRADE_SQL_CONNECTION_STRING = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'.format(
    '{ODBC Driver 17 for SQL Server}',
    config.SQL_SERVER_IP,
    'O2JAMTRADE',
    config.SQL_ACCOUNT_ID,
    config.SQL_ACCOUNT_PASSWORD
)

o2jam_sql_connection = pyodbc.connect(O2JAM_SQL_CONNECTION_STRING)
o2jamtrade_sql_connection = pyodbc.connect(O2JAMTRADE_SQL_CONNECTION_STRING)


def get_sql_console():
    return o2jam_sql_connection.cursor()

def get_sql_console_trade():
    return o2jamtrade_sql_connection.cursor()