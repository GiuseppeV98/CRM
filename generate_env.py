import secrets
import os

def generate_secret_key(length=50):
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(length))

def update_env_file(secret_key):
    # Controlla se il file .env esiste già
    if os.path.exists('.env'):
        with open('.env', 'a') as f:  # Usa 'a' per appendere invece di 'w' per sovrascrivere
            f.write(f"DJANGO_SECRET_KEY='{secret_key}'\n")
        print("DJANGO_SECRET_KEY aggiunta al file .env esistente.")
    else:
        with open('.env', 'w') as f:
            f.write(f"DJANGO_SECRET_KEY='{secret_key}'\n")
            # Aggiungi qui altre variabili d'ambiente se necessario
            # f.write("DATABASE_URL=postgres://user:password@localhost:5432/mydatabase\n")
        print(".env creato con successo con la nuova DJANGO_SECRET_KEY.")

if __name__ == "__main__":
    secret_key = generate_secret_key()
    update_env_file(secret_key)
