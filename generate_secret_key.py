#!/usr/bin/env python
"""
Script to generate a new Django secret key.
Run this script and copy the output to your .env file.

Usage: python generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("=" * 60)
    print("NEW SECRET KEY GENERATED")
    print("=" * 60)
    print(f"SECRET_KEY={secret_key}")
    print("=" * 60)
    print("Copy the line above to your .env file")
    print("NEVER share this key or commit it to version control!")
    print("=" * 60)
