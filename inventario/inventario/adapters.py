from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
