from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile,User
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.mail import send_mail
import pyotp
import qrcode
import base64
import secrets
import hashlib
import requests
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import signing

# Form per l'inserimento del codice OTP
class OTPForm(forms.Form):
    otp_code = forms.CharField(label='Codice OTP', max_length=6)


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.user.is_authenticated:
        return redirect('two_factor_auth:verify_otp')

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user_attempt = User.objects.filter(username=email).first()
        if user_attempt:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=user_attempt)
            except Exception as e:
                return render(request, 'login.html', {'form': form})

            if not profile.can_attempt_login():
                form.add_error(None, "Troppi tentativi di accesso falliti. Riprova più tardi.")
                return render(request, 'login.html', {'form': form})
            
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)  # Assicurati di fare il login prima di manipolare la sessione
                request.session.cycle_key()

                profile.reset_failed_login_attempts()  # Reset dei tentativi falliti
                profile.last_check_token= timezone.now()
                profile.save()              #aggiorno solo il last_check_token al primo accesso ---------------------
                if not profile.two_factor_secret:
                    return redirect('two_factor_auth:generate_qr')
                else:
                    request.session['verified_2fa'] = False  # Resetta il flag di verifica
                    return redirect('two_factor_auth:verify_otp')
            else:
                profile.register_failed_login()  # Registra il tentativo fallito

    return render(request, 'login.html', {'form': form})

@login_required
def generate_qr_code(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    qr_image_base64 = None
    if created or not profile.two_factor_secret:
        #profile.two_factor_secret = pyotp.random_base32()
        two_factor=pyotp.random_base32()
        profile.set_two_factor(two_factor)
        profile.save()

        # Il middleware si assicurerà che solo gli utenti che devono configurare 2FA vedano questa pagina.
        totp = pyotp.TOTP(two_factor)#profile.two_factor_secret)
        uri = totp.provisioning_uri(request.user.username, issuer_name="Adn CallCenter")
        qr = qrcode.make(uri)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

    # Passa l'immagine codificata in base64 al template
    return render(request, "generate_qr.html", {"qr_image_base64": qr_image_base64})

@login_required
def verify_otp(request):
    form = OTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        profile = UserProfile.objects.get(user=request.user)
        totp = pyotp.TOTP(profile.get_two_factor())#in caso di crypting ricorda di decodificare prima
        if totp.verify(form.cleaned_data['otp_code']):
            request.session['verified_2fa'] = True
            request.session['token_2fa'] = profile.two_factor_secret
            # Regenera il session_token dopo la verifica dell'OTP per mantenere l'integrità della sessione
            new_session_token = secrets.token_urlsafe()
            profile.set_session_token(new_session_token)
            profile.save()
            #new_session_token = signing.dumps(new_session_token)
            #profile.session_token = new_session_token
            profile.last_check_token = timezone.now()
            profile.save()
            #request.session['session_token'] = new_session_token
            #encrypted_token = signing.dumps(new_session_token)
            request.session['session_token'] = profile.session_token#new_session_token#########
            #return redirect('dashboard:homepage')
            # Effettua una richiesta POST al progetto ASP con il session_token
            url_asp = 'https://crm.adncallcenter.net/default.asp'
            data = {'session_token': new_session_token}
            try:
                #print("Invio dei dati a:", url_asp)
                #print("Dati inviati:", data)
                response = requests.post(url_asp, data=data)              
                print("Status code della risposta:", response.status_code)
                #print("Testo della risposta:", response.text)
            
            except requests.RequestException as e:
                error_message = f'Errore nella comunicazione con il progetto ASP: {e}'
                form.add_error(None, error_message)
                return render(request, 'verify_otp.html', {'form': form})

            # Reindirizza l'utente al progetto ASP dopo l'invio del token
            return redirect(url_asp)
        else:
            # Se il codice OTP non è corretto, mostra un errore.
            form.add_error('otp_code', 'Codice OTP non valido.')
            
    # Se il metodo non è POST o il form non è valido, mostra semplicemente la pagina.
    return render(request, 'verify_otp.html', {'form': form})


def send_otp(utente):
    otp = pyotp.TOTP(utente.profile.two_factor_secret).now()
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()  # Calcolo dell'hash dell'OTP
    utente.profile.email_otp = otp_hash
    utente.profile.otp_timestamp = timezone.now()
    utente.profile.save()
    send_mail(
        'Il tuo codice OTP',
        f'Il tuo codice OTP è: {otp}. Valido per 1 minuti.',
        'noreply@esempio.com',
        [utente.email],
        fail_silently=False,
    )

# Funzione per verificare l'OTP inviato dall'utente
#modifica effettuata su profile al posto di utente e aggiunto aggiornamento della sessione 
#e dell'ora del last_check_token
def verify_mail_otp(utente, otp_fornito):
    otp_fornito = hashlib.sha256(otp_fornito.encode()).hexdigest()
    tempo_corrente = timezone.now()
    tempo_valido = utente.profile.otp_timestamp + timedelta(minutes=1)  # 1 minuti di validità
    if (otp_fornito == utente.profile.email_otp and tempo_corrente <= tempo_valido):
        # Resetta i valori dell'OTP nel database
        utente.profile.email_otp = ''
        utente.profile.otp_timestamp = None
        utente.profile.save()
        
        return True
    else:
        return False  # OTP non valido o scaduto

def homepage(request):
    if not request.user.is_authenticated or not request.session.get('verified_2fa', False):
        return redirect('login')
    return render(request, 'dashboard:homepage')

def user_logout(request):
    logout(request)
    return redirect('two_factor_auth:login')

@login_required
def send_and_redirect_to_verify_backup(request):
    user = request.user
    send_otp(user)
    #messages.info(request, "Un codice OTP è stato inviato alla tua email. Utilizzalo per verificare la tua identità.")
    return redirect('two_factor_auth:verify_backup')

@login_required
def verify_backup(request):
    if request.method == 'POST':
        otp_provided = request.POST.get('backup_code', '')
        user = request.user
        if verify_mail_otp(user, otp_provided):
            # Imposta la sessione come autenticata per il 2FA o esegui altre azioni necessarie
            profile = UserProfile.objects.get(user=request.user)
            request.session['verified_2fa'] = True
            request.session['token_2fa'] = profile.two_factor_secret
            new_session_token = secrets.token_urlsafe()
            #new_session_token = signing.dumps(new_session_token)
            #profile.session_token = new_session_token
            profile.set_session_token(new_session_token)
            #profile.save()
            profile.last_check_token = timezone.now()
            profile.save()
            request.session['session_token'] = new_session_token
            return redirect('dashboard:homepage')
        else:
            messages.error(request, "OTP non valido o scaduto.")
    return render(request, 'verify_backup.html')





#utilizza per evitare il seguente errore Forbidden (CSRF cookie not set.): /auth/verify-token/


@csrf_exempt
def verify_token(request):
    token_value = None

    if request.method == 'POST':
        token_value = request.POST.get('token')
    elif request.method == 'GET':
        token_value = request.GET.get('token')
    else:
        return HttpResponse('Invalid request method', status=400)

    #if token_value:
        # Cripta il token_value ricevuto
        #encrypted_token_value = signing.dumps(token_value)
        
    user_profiles = UserProfile.objects.filter(session_token=token_value)
    if user_profiles.exists():
        profile = user_profiles.first()
        tempo_corrente = timezone.now()
        tempo_valido = profile.last_check_token + timedelta(minutes=10)

        if tempo_corrente <= tempo_valido:
            profile.last_check_token = timezone.now()  # Aggiorna last_check_token con l'ora corrente
            profile.save()
            return HttpResponse('True')
        else:
            return HttpResponse('False', status=403)

    return HttpResponse('False', status=404)
#controllare token se il token è scaduto allora fai effettuare l'accesso normalmente, mentre se 
#il token è ancora valido chiedi con il pop up