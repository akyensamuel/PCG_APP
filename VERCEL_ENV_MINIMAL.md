# Minimal Required Environment Variables for Vercel

## Essential Variables (Must Set)
```
SECRET_KEY=your-new-production-secret-key
DEBUG=False
ALLOWED_HOSTS=.vercel.app
```

## Database Variables (Required for PostgreSQL)
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.dwhjrmllybfrxpgajpxi
DB_PASSWORD=bn46XtQ2-b%GPd+
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=6543
```

## Security Variables (Recommended)
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Optional Variables (Can Skip Initially)
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
TIME_ZONE=UTC
STATIC_URL=/static/
MEDIA_URL=/media/
```

## Quick CLI Setup (Copy & Paste)
```bash
# Essential
vercel env add SECRET_KEY production
vercel env add DEBUG production  
vercel env add ALLOWED_HOSTS production

# Database
vercel env add DB_ENGINE production
vercel env add DB_NAME production
vercel env add DB_USER production
vercel env add DB_PASSWORD production
vercel env add DB_HOST production
vercel env add DB_PORT production

# Security
vercel env add SECURE_SSL_REDIRECT production
vercel env add SESSION_COOKIE_SECURE production
vercel env add CSRF_COOKIE_SECURE production
```

Total: **12 variables** instead of 22+
