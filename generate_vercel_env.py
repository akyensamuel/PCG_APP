#!/usr/bin/env python
"""
Script to generate environment variables for Vercel deployment.
This script reads your .env file and outputs Vercel CLI commands
to set environment variables.

Usage: python generate_vercel_env.py
"""

import os
from pathlib import Path

def generate_vercel_env_commands():
    """Generate Vercel CLI commands for setting environment variables."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Make sure you're in the project root directory.")
        return
    
    print("🚀 Vercel Environment Variable Setup Commands")
    print("=" * 60)
    print("Run these commands in your terminal after installing Vercel CLI:")
    print("npm i -g vercel")
    print("vercel login")
    print("vercel link")
    print()
    
    # Read .env file and generate commands
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    production_overrides = {
        'DEBUG': 'False',
        'ALLOWED_HOSTS': '.vercel.app',
        'SECURE_SSL_REDIRECT': 'True',
        'SESSION_COOKIE_SECURE': 'True',
        'CSRF_COOKIE_SECURE': 'True',
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend'
    }
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Apply production overrides
            if key in production_overrides:
                value = production_overrides[key]
            
            # Skip empty values for optional settings
            if not value and key in ['EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']:
                continue
                
            print(f'vercel env add {key} production')
            
    print()
    print("📝 Notes:")
    print("- You'll be prompted to enter the value for each variable")
    print("- For SECRET_KEY, generate a new one using: python generate_secret_key.py")
    print("- Make sure to set DEBUG=False for production")
    print("- Update ALLOWED_HOSTS to include your Vercel domain")
    print()
    print("🔐 Security Reminder:")
    print("- Never commit production secrets to version control")
    print("- Use different secrets for production vs development")
    print("- Regularly rotate your secret keys and passwords")

if __name__ == "__main__":
    generate_vercel_env_commands()
