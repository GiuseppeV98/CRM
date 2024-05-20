

from django.shortcuts import redirect
from django.urls import resolve
from two_factor_auth.models import UserProfile
from django.http import HttpResponseRedirect
from django.urls import reverse

class TwoFactorAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
        
            profile = UserProfile.objects.get(user=request.user)
            current_url_name = resolve(request.path).url_name
            # Verifica se il token di sessione corrisponde
            session_token = request.session.get('session_token')
            if request.session.get('verified_2fa', False):
                if profile.session_token != session_token:
            
            # Solo se l'utente ha verificato 2FA e il token non corrisponde, effettua il logout
                    return redirect('two_factor_auth:logout')

            if request.session.get('verified_2fa', False) and current_url_name in ['generate_qr', 'verify_otp','verify_backup']:
                return redirect('dashboard:homepage')

            if current_url_name != 'homepage' and request.session.get('verified_2fa', False):
            # Se l'utente ha verificato l'OTP, non dovrebbe essere reindirizzato altrove.
                return response
            # Assicurati che l'utente completi la configurazione 2FA prima di accedere alla homepage
            if current_url_name == 'homepage':
                if not request.session.get('verified_2fa', False):
                    # Reindirizza a generate_qr o verify_otp in base alla configurazione del segreto 2FA
                    if not profile.two_factor_secret:
                        return redirect('two_factor_auth:generate_qr')
                    else:
                        return redirect('two_factor_auth:verify_otp')

            # Gestisci il flusso tra la generazione del QR e la verifica OTP
            
            if current_url_name == 'generate_qr':
                if profile.two_factor_secret and not request.session.get('two_factor_token'):
                # Accesso a generate_qr solo se esiste un token nella sessione
                    # Senza token, reindirizza a verify_otp
                    return redirect('two_factor_auth:verify_otp')
             
        return response


