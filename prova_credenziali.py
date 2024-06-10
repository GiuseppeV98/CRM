from ldap3 import Server, Connection, ALL

ldap_server = '192.168.1.2'  
ldap_port = 389
user_email = 'TestLdap@corporate.it' 
user_password = 'T3st@Ld4p'  

try:
    server = Server(ldap_server, port=ldap_port, get_info=ALL)
    conn = Connection(server,
                      user=user_email,  
                      password= user_password,
                      auto_bind=True)
    
    if conn.bind():
        print("Autenticazione al server LDAP riuscita.")
    else:
        print("Autenticazione al server LDAP fallita.")
except Exception as e:
    print(f"Errore nell'autenticazione al server LDAP: {e}")
