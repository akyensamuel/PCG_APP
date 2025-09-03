# Environment Configuration Guide

## Overview
This project uses python-decouple to manage environment variables securely. This keeps sensitive information like secret keys and database credentials out of version control.

## Setup Instructions

### 1. Copy the Example Environment File
```bash
cp .env.example .env
```

### 2. Update the .env File
Edit the `.env` file with your actual configuration values:

- **SECRET_KEY**: Generate a new secret key for production
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Add your domain names for production
- **Database settings**: Configure based on your database choice
- **Email settings**: Configure for your email provider

### 3. Generate a New Secret Key (for Production)
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Environment Variables Reference

### Core Django Settings
- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Enable/disable debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames

### Database Configuration
- `DB_ENGINE`: Database backend (sqlite3, postgresql, mysql)
- `DB_NAME`: Database name (leave empty for SQLite)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

### Email Configuration
- `EMAIL_BACKEND`: Email backend to use
- `EMAIL_HOST`: SMTP server hostname
- `EMAIL_PORT`: SMTP server port
- `EMAIL_USE_TLS`: Use TLS encryption (True/False)
- `EMAIL_HOST_USER`: Email username
- `EMAIL_HOST_PASSWORD`: Email password or app-specific password

### Security Settings (Production)
- `SECURE_BROWSER_XSS_FILTER`: Enable XSS filter
- `SECURE_CONTENT_TYPE_NOSNIFF`: Prevent MIME type sniffing
- `X_FRAME_OPTIONS`: Clickjacking protection
- `SECURE_SSL_REDIRECT`: Force HTTPS redirects
- `SESSION_COOKIE_SECURE`: Secure session cookies
- `CSRF_COOKIE_SECURE`: Secure CSRF cookies

## Database Setup Examples

### SQLite (Development - Default)
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### PostgreSQL (Production)
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pcg_production
DB_USER=pcg_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432
```

### MySQL
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=pcg_production
DB_USER=pcg_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=3306
```

## Email Setup Examples

### Development (Console Backend)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Gmail SMTP
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_specific_password
```

### SendGrid
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
```

## Security Best Practices

1. **Never commit .env files** - They're already in .gitignore
2. **Use strong secret keys** - Generate new ones for each environment
3. **Enable security settings in production** - Set SECURE_* settings to True
4. **Use environment-specific configurations** - Different .env for dev/staging/prod
5. **Rotate credentials regularly** - Update passwords and API keys periodically

## Deployment Notes

For production deployment:
1. Set `DEBUG=False`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Enable all security settings
5. Use HTTPS (`SECURE_SSL_REDIRECT=True`)
6. Use secure cookie settings
7. Configure proper email backend for notifications
