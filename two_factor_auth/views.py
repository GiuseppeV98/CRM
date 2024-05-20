from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile,User
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
import pyotp
import qrcode
import base64
import secrets
import hashlib
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages



# Form per l'inserimento del codice OTP
class OTPForm(forms.Form):
    otp_code = forms.CharField(label='Codice OTP', max_length=6)

# Vista per il login semplice

def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.user.is_authenticated:
        return redirect('two_factor_auth:verify_otp')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_attempt = User.objects.filter(username=username).first()

        if user_attempt:
            profile, _ = UserProfile.objects.get_or_create(user=user_attempt)
            if not profile.can_attempt_login():
                form.add_error(None, "Troppi tentativi di accesso falliti. Riprova più tardi.")
                return render(request, 'login.html', {'form': form})
            
            user = authenticate(username=username, password=password)
            if user:
                            
                login(request, user)  # Assicurati di fare il login prima di manipolare la sessione
                request.session.cycle_key()

                profile.reset_failed_login_attempts()  # Reset dei tentativi falliti

                if not profile.two_factor_secret:
                    return redirect('two_factor_auth:generate_qr')
                else:
                    request.session['verified_2fa'] = False  # Resetta il flag di verifica
                    # Genera un nuovo token di sessione solo se non esiste già
                    # Genera e aggiorna il session_token solo al primo accesso
                    if not request.session.get('session_token'):
                        session_token = secrets.token_urlsafe()
                        profile.session_token = session_token
                        profile.save()
                        request.session['session_token'] = session_token

                    return redirect('two_factor_auth:verify_otp')

            else:
                profile.register_failed_login()  # Registra il tentativo fallito
                #form.add_error(None, "Username o password non validi.")
        #else:
            #form.add_error(None, "Username o password non validi.")

    return render(request, 'login.html', {'form': form})
@login_required
def generate_qr_code(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if created or not profile.two_factor_secret:
        profile.two_factor_secret = pyotp.random_base32()
        profile.save()
        token = secrets.token_urlsafe()
        request.session['two_factor_token'] = token

    # Il middleware si assicurerà che solo gli utenti che devono configurare 2FA vedano questa pagina.
    totp = pyotp.TOTP(profile.two_factor_secret)
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
        totp = pyotp.TOTP(profile.two_factor_secret)
        if totp.verify(form.cleaned_data['otp_code']):
            request.session['verified_2fa'] = True
            # Regenera il session_token dopo la verifica dell'OTP per mantenere l'integrità della sessione
            new_session_token = secrets.token_urlsafe()
            profile.session_token = new_session_token
            profile.save()
            request.session['session_token'] = new_session_token
            return redirect('dashboard:homepage')
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
        f'Il tuo codice OTP è: {otp}. Valido per 10 minuti.',
        'noreply@esempio.com',
        [utente.email],
        fail_silently=False,
    )

# Funzione per verificare l'OTP inviato dall'utente
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
    
@login_required
def request_email_otp(request):
    user = request.user
    send_otp(user)
    messages.success(request, "OTP inviato via email. Controlla la tua posta.")
    return redirect('two_factor_auth:verify_backup')

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
            request.session['verified_2fa'] = True
            return redirect('dashboard:homepage')
        else:
            messages.error(request, "OTP non valido o scaduto.")
    return render(request, 'verify_backup.html')