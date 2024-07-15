from django.urls import path
from .views import user_login, generate_qr_code, verify_otp, verify_backup, user_logout,send_and_redirect_to_verify_backup,verify_token

app_name = 'two_factor_auth'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('generate_qr/', generate_qr_code, name='generate_qr'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('verify_backup/', verify_backup, name='verify_backup'),
    path('send_otp_and_redirect/', send_and_redirect_to_verify_backup, name='send_otp_and_redirect'),
    path('logout/', user_logout, name='logout'),
    path('verify-token/', verify_token, name='verify_token'),
]
