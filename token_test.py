import os
import django

# Imposta DJANGO_SETTINGS_MODULE nel modulo delle impostazioni della tua applicazione Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

# Inizializza Django
django.setup()

from django.core import signing

def test_token_signing_and_loading():
    # Token da firmare
    token = 'il_tuo_token_da_firmare'

    # Firma il token
    signed_token = signing.dumps(token)
    print("Token firmato:", signed_token)

    try:
        # Decodifica il token firmato
        original_token = signing.loads(signed_token)
        print("Token decodificato:", original_token)
    except signing.BadSignature:
        print("Errore: il token non è valido o la firma è stata alterata.")

if __name__ == "__main__":
    test_token_signing_and_loading()
