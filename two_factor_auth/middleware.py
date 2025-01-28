from django.shortcuts import redirect
from django.urls import resolve
from two_factor_auth.models import UserProfile
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core import signing
from django.utils import timezone
from datetime import timedelta

class TwoFactorAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        return response

