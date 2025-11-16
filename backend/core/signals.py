"""
Signals for OAuth authentication and user management
"""
from django.dispatch import receiver
from django.contrib.auth import login
from django.contrib.auth.models import User
from allauth.socialaccount.signals import pre_social_login, social_account_added
import logging

logger = logging.getLogger(__name__)


@receiver(pre_social_login)
def on_pre_social_login(sender, request, sociallogin, **kwargs):
    """
    Signal handler called before social login.
    Links social account to existing user if email matches.
    """
    email_address = sociallogin.account.extra_data.get('email')
    
    if email_address:
        try:
            user = User.objects.get(email=email_address)
            sociallogin.connect(request, user)
            logger.info(f"Linked social account to existing user: {email_address}")
        except User.DoesNotExist:
            logger.info(f"No existing user found for email: {email_address}")
    
    # If user exists, ensure they're logged in
    if sociallogin.user and sociallogin.user.pk:
        login(request, sociallogin.user, backend='allauth.account.auth_backends.AuthenticationBackend')
        request.session.save()
        logger.info(f"User {sociallogin.user.email} logged in via signal. Session: {request.session.session_key}")


@receiver(social_account_added)
def on_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Signal handler called after social account is added.
    Ensures session is saved and user is properly authenticated.
    """
    logger.info(f"Social account added for user: {sociallogin.user.email}")
    
    # Ensure user is logged in
    if not request.user.is_authenticated:
        login(request, sociallogin.user, backend='allauth.account.auth_backends.AuthenticationBackend')
    
    # Force save session
    request.session.save()
    logger.info(f"Session saved: {request.session.session_key}")

