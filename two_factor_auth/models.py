from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.core import signing


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_secret = models.CharField(max_length=100, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login_attempt = models.DateTimeField(null=True, blank=True)
    session_token = models.CharField(max_length=255, blank=True)
    last_check_token = models.DateTimeField(null=True, blank=True)
    email_otp = models.CharField(max_length=64, blank=True, null=True)  # Hash dell'OTP  , 
    otp_timestamp = models.DateTimeField(null=True, blank=True)
    
    def set_session_token(self, token):
        self.session_token = signing.dumps(token)

    def get_session_token(self):
        return signing.loads(self.session_token)
    
    def set_two_factor(self, token):
        self.two_factor_secret = signing.dumps(token)

    def get_two_factor(self):
        return signing.loads(self.two_factor_secret)
    
    def can_attempt_login(self):
        max_attempts = 5
        reset_time = 10

        if self.failed_login_attempts < max_attempts:
            return True
        elif self.last_failed_login_attempt and timezone.now() > self.last_failed_login_attempt + datetime.timedelta(minutes=reset_time):
            self.failed_login_attempts = 0
            self.last_failed_login_attempt = None
            self.save()
            return True
        else:
            return False

    def register_failed_login(self):
        try:
            self.failed_login_attempts += 1
            self.last_failed_login_attempt = timezone.now()
            self.save()
            print(f"Failed login attempts: {self.failed_login_attempts}")
            print(f"Last failed login attempt: {self.last_failed_login_attempt}")
        except Exception as e:
            print(f"Error occurred: {e}")


        #Azzera i tentativi di login falliti
    def reset_failed_login_attempts(self):
        self.failed_login_attempts = 0
        self.last_failed_login_attempt = None
        self.save()

    