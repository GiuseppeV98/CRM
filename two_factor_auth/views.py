from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User,UserProfile
from .forms import OTPForm
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.mail import send_mail
import pyotp
import qrcode
import base64
import secrets
import hashlib
#import requests
from django.http import JsonResponse    
from django.utils import timezone
from datetime import timedelta
#from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import signing
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# Form per l'inserimento del codice OTP

@ensure_csrf_cookie
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            if "@corporate.it" not in username:
                username = f"{username}@corporate.it"
                print(username)

            password = data.get('password')
            user_attempt = User.objects.filter(username=username).first()
            print(f"user_attempt: {user_attempt}")

            # Tentativo di autenticazione tramite LDAP
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # Creazione automatica del profilo se l'utente si autentica correttamente
                profile, _ = UserProfile.objects.get_or_create(user=user)
                request.session.cycle_key()
                profile.reset_failed_login_attempts()
                profile.last_check_token = timezone.now()
                profile.save()
                request.session['ppw'] = password 
                print("nella sessione:", request.session['ppw'])
                print("Login successful, user logged in")

                if not (profile.complete_config):
                    return JsonResponse({'redirect': 'generate_qr'}, status=200)
                else:
                    request.session['verified_2fa'] = False
                    return JsonResponse({'redirect': 'verify_otp'}, status=200)
            else:
                # Se l'utente non è autenticato, registra il tentativo fallito
                if user_attempt:
                    profile, _ = UserProfile.objects.get_or_create(user=user_attempt)
                    profile.register_failed_login()
                print("User not found or invalid credentials")
                return JsonResponse({'error': 'Credenziali non valide o utente non trovato'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    elif request.method == 'GET':
        return JsonResponse({'status': 'success', 'message': 'Login page accessible'}, status=200)
    
    else:
        return JsonResponse({'status': 'error', 'message': 'Metodo non permesso'}, status=405)


    
@login_required
@ensure_csrf_cookie
def generate_qr_code(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    qr_image_base64 = None
    two_factor = pyotp.random_base32()
    profile.set_two_factor(two_factor)
    profile.save()
    
    totp = pyotp.TOTP(two_factor)
    uri = totp.provisioning_uri(request.user.username, issuer_name="Adn CallCenter D+R")
    qr = qrcode.make(uri)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    qr_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return JsonResponse({"qr_image_base64": qr_image_base64})           

@ensure_csrf_cookie
@login_required
def complete_config(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_value = data.get('otp') 
        print(f"OTP ricevuto: {otp_value}")
        if otp_value:
            profile = UserProfile.objects.get(user=request.user)
            totp = pyotp.TOTP(profile.get_two_factor())
            if totp.verify(otp_value):
                profile.complete_config = True
                profile.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'fail', 'message': 'Codice OTP non valido.'})
    return JsonResponse({'status': 'fail', 'message': 'Metodo non consentito.'}, status=405)


@ensure_csrf_cookie
@login_required
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            otp_code = data.get('otp_code')
            print(f"OTP ricevuto: {otp_code}")
            profile = UserProfile.objects.get(user=request.user)
            print(f"UserProfile trovato: {profile}")
            if not profile.can_attempt_login():
                return JsonResponse({'status': 'fail', 'error': 'Troppi tentativi di accesso falliti. Riprova più tardi.'}, status=403)
            totp = pyotp.TOTP(profile.get_two_factor())
            expected_otp = totp.now()
            print(f"OTP atteso: {expected_otp}")
            print(f"Segreto 2FA: {profile.get_two_factor()}")
            if totp.verify(otp_code):
                request.session.cycle_key()
                request.session['verified_2fa'] = True
                print("OTP verificato con successo")
                new_session_token = secrets.token_urlsafe()
                profile.set_session_token(new_session_token)
                profile.last_check_token = timezone.now()
                profile.save()
                ppw = request.session['ppw']
                del request.session['ppw']
                request.session['session_token'] = profile.session_token
                request.session['token_2fa'] = profile.two_factor_secret
                url_asp = 'https://crm.adncallcenter.net/training/defaultnew.asp'#'/dashboard'  # Modificato per redirect alla dashboard
                print(f"Redirecting to {url_asp}")
                return JsonResponse({
                    'status': 'success',
                    'session_token': profile.session_token,
                    'user': profile.user.username,
                    'password': ppw,
                    'redirect': url_asp
                }, status=200)
            
            else:
                profile.register_failed_login()
                print("OTP non valido")
                return JsonResponse({'status': 'fail', 'error': 'OTP non valido'}, status=401)
        except Exception as e:
            print(f"Error during OTP verification: {e}")
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'fail', 'message': 'Method not allowed'}, status=405)

# def homepage(request):
#    if not request.user.is_authenticated or not request.session.get('verified_2fa', False):
#        return redirect('login')
#    return render(request, 'dashboard:homepage')


@ensure_csrf_cookie
@login_required
def send_otp_and_redirect(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    otp = pyotp.TOTP(profile.get_two_factor()).now()
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    profile.email_otp = otp_hash
    profile.otp_timestamp = timezone.now()
    profile.save()
    print(f"Inviando email a {user.email} con OTP {otp}")
    send_mail(
        'Il tuo codice OTP',
        f'Il tuo codice OTP è: {otp}. Valido per 1 minuto.',
        'noreply@esempio.com',
        [user.email],
        fail_silently=False,
    )
    return JsonResponse({'status': 'success'})

@ensure_csrf_cookie
@login_required
def verify_backup_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_provided = data.get('otp', '')
        print(f"OTP fornito: '{otp_provided}'")  # Assicurati che l'OTP sia non vuoto
        if not otp_provided:
            return JsonResponse({'error': 'OTP non fornito'}, status=400)

        user = request.user
        profile = UserProfile.objects.get(user=user)

        otp_provided_hash = hashlib.sha256(otp_provided.encode()).hexdigest()
        print(f"OTP hashato: {otp_provided_hash}")
        print(f"OTP nel profilo: {profile.email_otp}")

        tempo_corrente = timezone.now()
        tempo_valido = profile.otp_timestamp + timedelta(minutes=1)
        print(f"Tempo corrente: {tempo_corrente}, Tempo valido: {tempo_valido}")

        if otp_provided_hash == profile.email_otp and tempo_corrente <= tempo_valido:
            profile.email_otp = ''
            profile.otp_timestamp = None
            profile.reset_failed_login_attempts()
            profile.save()
            request.session['verified_2fa'] = True
            ppw = request.session['ppw']
            del request.session['ppw']
            print("OTP verificato con successo, redirect a /dashboard")
            url_asp = 'https://crm.adncallcenter.net/training/defaultnew.asp'#'/dashboard'  # Modificato per redirect alla dashboard
            return JsonResponse({
                    'status': 'success',
                    'session_token': profile.session_token,
                    'user': profile.user.username,
                    'password': ppw,
                    'redirect': url_asp
                }, status=200)
            #return JsonResponse({'status': 'success', 'redirect': '/dashboard'})
        else:
            print("OTP non valido o scaduto")
            profile.register_failed_login()
            return JsonResponse({'error': 'OTP non valido o scaduto'}, status=401)
    print("Richiesta non valida")
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def verify_token(request):
    token_value = None
    
    token_value = request.POST.get('token')
    if token_value is None:
        return HttpResponse('Token non valido', status=400)
    else:
        
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
                return HttpResponse('True', status=200)
            else:
                return HttpResponse('False', status=403)
    return HttpResponse('False', status=404)

def user_logout(request):
    request.session.pop('verified_2fa', None)
    request.session.pop('session_token', None)
    request.session.pop('token_2fa',None)
    print("classico logout")

    # Esegui il logout dell'utente
    logout(request)
    request.session.flush() 
    # Restituisci una risposta JSON al client React
    return JsonResponse({'status': 'success', 'message': 'Logout successful'}, status=200)

def asp_user_logout(request):
    request.session.pop('verified_2fa', None)
    request.session.pop('session_token', None)
    request.session.pop('token_2fa',None)
    print("asp_logout")
    # Esegui il logout dell'utente
    logout(request)
    
    # Restituisci una risposta JSON al client React
    return redirect('http://172.23.149.57:3000/login')
@ensure_csrf_cookie
@login_required
def get_user_email(request):
    email = request.user.email
    email_presente = bool(email)  # Restituisce True se l'email esiste, altrimenti False
    return JsonResponse({"email_presente": email_presente})