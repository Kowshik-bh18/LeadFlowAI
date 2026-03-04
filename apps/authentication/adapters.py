from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
import uuid


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.organization = form.cleaned_data.get('organization', '')
        if commit:
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Auto-generate username from email if not set
        if not user.username:
            user.username = user.email.split('@')[0] + '_' + str(uuid.uuid4())[:8]
            user.save()
        return user

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Auto-set username from email
        if not user.username:
            base = (data.get('email') or '').split('@')[0]
            user.username = base + '_' + str(uuid.uuid4())[:8]
        return user