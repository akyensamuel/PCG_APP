# Vercel Deployment Guide for PCG App

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Environment Variables**: Prepare your production environment variables

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect it's a Python project

### 2. Configure Environment Variables

In your Vercel project dashboard, go to Settings > Environment Variables and add:

#### Required Variables:
```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.vercel.app
```

#### Database Configuration (Supabase):
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.dwhjrmllybfrxpgajpxi
DB_PASSWORD=bn46XtQ2-b%GPd+
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=6543
```

#### Email Configuration:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Security Settings:
```env
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
TIME_ZONE=UTC
STATIC_URL=/static/
MEDIA_URL=/media/
```

### 3. Generate Production Secret Key

Run this command locally and use the output as your SECRET_KEY:

```bash
python generate_secret_key.py
```

### 4. Deploy

1. Push your code to GitHub
2. Vercel will automatically trigger a deployment
3. Monitor the build logs in Vercel dashboard

## Build Process

The `vercel.json` configuration handles:

1. **Python Build**: Installs dependencies and runs Django
2. **Static Build**: Builds Tailwind CSS and collects static files
3. **Routing**: Configures URL routing for Django app and static files
4. **Environment**: Sets production environment variables

## Build Commands

- **Install**: `pip install -r requirements.txt && npm install`
- **Build**: `npm run tailwind:build && python manage.py collectstatic --noinput`
- **Start**: Serverless function handles Django WSGI

## File Structure for Vercel

```
project/
├── vercel.json          # Vercel configuration
├── build.sh             # Build script (optional)
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── PCG_APP/
│   ├── wsgi.py         # WSGI application entry point
│   ├── settings.py     # Django settings with env vars
│   └── static/         # Static files
└── static/             # Collected static files
```

## Troubleshooting

### Common Issues:

1. **Build Timeouts**: 
   - Reduce dependencies
   - Use `maxLambdaSize: "15mb"` in vercel.json

2. **Static Files Not Loading**:
   - Check `STATIC_URL` and `STATIC_ROOT` settings
   - Ensure `collectstatic` runs in build process

3. **Database Connection Issues**:
   - Verify environment variables are set correctly
   - Check database host accessibility

4. **Secret Key Errors**:
   - Generate a new secret key for production
   - Ensure it's set in Vercel environment variables

### Build Logs

Monitor build logs in Vercel dashboard:
- Check for Python/Node.js installation errors
- Verify Tailwind CSS compilation
- Confirm static file collection

## Post-Deployment

1. **Database Migration**: Run migrations manually first time:
   ```bash
   python manage.py migrate
   ```

2. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Test Functionality**:
   - Check all pages load correctly
   - Test user authentication
   - Verify database operations

## Performance Optimization

1. **Static Files**: Use Vercel's CDN for static assets
2. **Database**: Optimize queries and use connection pooling
3. **Caching**: Implement Django caching for better performance
4. **Monitoring**: Use Vercel Analytics and Django logging

## Security Checklist

- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY
- ✅ HTTPS enforced (SECURE_SSL_REDIRECT=True)
- ✅ Secure cookies enabled
- ✅ Database credentials in environment variables
- ✅ No sensitive data in repository

Your Django app is now ready for production deployment on Vercel! 🚀
