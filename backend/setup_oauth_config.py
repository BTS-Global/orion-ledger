#!/usr/bin/env python3
"""
OAuth Configuration Script for Django Allauth
============================================

This script configures OAuth providers (Google, Microsoft) for the accounting software.
It handles both setup instructions and actual configuration.

Usage:
    python setup_oauth_config.py --setup     # Show setup instructions
    python setup_oauth_config.py --config    # Configure with environment variables
    python setup_oauth_config.py --help      # Show this help

Environment Variables Required for --config:
    GOOGLE_CLIENT_ID       - Google OAuth Client ID
    GOOGLE_CLIENT_SECRET   - Google OAuth Client Secret  
    MICROSOFT_CLIENT_ID    - Microsoft OAuth Application ID
    MICROSOFT_CLIENT_SECRET - Microsoft OAuth Client Secret
    SITE_DOMAIN           - Domain for the site (optional, defaults to localhost)
"""

import os
import sys
import django
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


def show_setup_instructions():
    """Display setup instructions for OAuth providers."""
    print("\n" + "="*70)
    print(" OAUTH SETUP INSTRUCTIONS")
    print("="*70)
    
    print("\n📌 GOOGLE OAUTH SETUP")
    print("-" * 30)
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable 'Google+ API'")
    print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client ID'")
    print("5. Application type: Web application")
    print("6. Authorized redirect URIs:")
    print("   - http://localhost:8000/accounts/google/login/callback/")
    print("   - https://YOUR-DOMAIN/accounts/google/login/callback/")
    print("7. Copy Client ID and Client Secret")
    
    print("\n📌 MICROSOFT OAUTH SETUP")
    print("-" * 30)
    print("1. Go to: https://portal.azure.com/")
    print("2. Navigate to 'Azure Active Directory' → 'App registrations'")
    print("3. Click 'New registration'")
    print("4. Name: Accounting Software")
    print("5. Supported account types: Accounts in any organizational directory and personal Microsoft accounts")
    print("6. Redirect URI: Web → http://localhost:8000/accounts/microsoft/login/callback/")
    print("7. After creation, go to 'Certificates & secrets'")
    print("8. Create a new client secret")
    print("9. Copy Application (client) ID and the secret value")
    
    print("\n📌 ENVIRONMENT VARIABLES")
    print("-" * 30)
    print("Create a .env file with:")
    print("GOOGLE_CLIENT_ID=your_google_client_id")
    print("GOOGLE_CLIENT_SECRET=your_google_client_secret")
    print("MICROSOFT_CLIENT_ID=your_microsoft_client_id")
    print("MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret")
    print("SITE_DOMAIN=your-domain.com  # optional")
    
    print("\n📌 ALTERNATIVE: Django Admin")
    print("-" * 30)
    print("1. Go to: http://localhost:8000/admin/")
    print("2. Navigate to 'Social applications'")
    print("3. Add new application for each provider")
    print("="*70 + "\n")


def configure_oauth():
    """Configure OAuth providers using environment variables."""
    
    # Get site configuration
    site_domain = os.getenv('SITE_DOMAIN', 'localhost:8000')
    
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': site_domain,
            'name': 'Accounting Software'
        }
    )
    
    if not created:
        site.domain = site_domain
        site.name = 'Accounting Software'
        site.save()
    
    print(f"✅ Site configured: {site.domain}")
    
    # Configure Google OAuth
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if google_client_id and google_client_secret:
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': google_client_id,
                'secret': google_client_secret,
            }
        )
        
        if not created:
            google_app.client_id = google_client_id
            google_app.secret = google_client_secret
            google_app.save()
        
        google_app.sites.add(site)
        print(f"✅ Google OAuth configured")
        print(f"   Redirect URI: https://{site.domain}/accounts/google/login/callback/")
    else:
        print("⚠️  Google OAuth not configured - missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
    
    # Configure Microsoft OAuth
    microsoft_client_id = os.getenv('MICROSOFT_CLIENT_ID')
    microsoft_client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
    
    if microsoft_client_id and microsoft_client_secret:
        microsoft_app, created = SocialApp.objects.get_or_create(
            provider='microsoft',
            defaults={
                'name': 'Microsoft',
                'client_id': microsoft_client_id,
                'secret': microsoft_client_secret,
            }
        )
        
        if not created:
            microsoft_app.client_id = microsoft_client_id
            microsoft_app.secret = microsoft_client_secret
            microsoft_app.save()
        
        microsoft_app.sites.add(site)
        print(f"✅ Microsoft OAuth configured")
        print(f"   Redirect URI: https://{site.domain}/accounts/microsoft/login/callback/")
    else:
        print("⚠️  Microsoft OAuth not configured - missing MICROSOFT_CLIENT_ID or MICROSOFT_CLIENT_SECRET")
    
    print("\n🎉 OAuth configuration completed!")


def main():
    parser = argparse.ArgumentParser(
        description='Configure OAuth providers for Django Allauth',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--setup', 
        action='store_true', 
        help='Show OAuth setup instructions'
    )
    parser.add_argument(
        '--config', 
        action='store_true', 
        help='Configure OAuth using environment variables'
    )
    
    args = parser.parse_args()
    
    if args.setup:
        show_setup_instructions()
    elif args.config:
        configure_oauth()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
