#from ldap3 import Server, Connection, ALL

#ldap_server = '192.168.1.2'
#ldap_port = 389

#try:
#    server = Server(ldap_server, port=ldap_port, get_info=ALL)
#    conn = Connection(server)
#    if conn.bind():
#        print("Connessione al server LDAP riuscita.")
#    else:
#        print("Connessione al server LDAP fallita.")
#except Exception as e:
#    print(f"Errore nella connessione al server LDAP: {e}")

import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-IEQV8TAD\SQLEXPRESS;"
    "DATABASE=prova_sqls;"
    "UID=sa;"
    "PWD=Peppe1998!;"
    "TrustServerCertificate=yes;"
)

try:
    with pyodbc.connect(conn_str) as conn:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")