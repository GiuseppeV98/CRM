from django.urls import path
from .views import user_login, generate_qr_code,complete_config, verify_otp,verify_backup_otp,asp_user_logout, user_logout,send_otp_and_redirect,verify_token, get_user_email

app_name = 'two_factor_auth'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('generate_qr/', generate_qr_code, name='generate_qr'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('send_otp_and_redirect/', send_otp_and_redirect, name='send_otp_and_redirect'),
    path('verify_backup_otp/', verify_backup_otp, name='verify_backup_otp'),
    path('logout/', asp_user_logout, name='logout'),
    path('logout_base/', user_logout, name='logout_base'),
    path('verify-token/', verify_token, name='verify_token'),
    path('get_user_email/', get_user_email, name='get_user_email'),
    path('complete_config/', complete_config, name='complete_config'),  # Nuova route

]
