# PCG - A.N.T (Django)

A church platform built with Django. This repo includes Tailwind CSS for styling.

## Quickstart

1. Python env
   - Create/activate a venv (Windows): `virtual\Scripts\activate` or your preferred venv name
   - Install deps: `pip install -r requirements.txt`

2. Node (for Tailwind)
   - Install Node 18+ and run: `npm install`
   - Build CSS once: `npm run tailwind:build`
   - Or watch: `npm run tailwind:watch`

3. Django
   - Run migrations: `python PCG_APP/manage.py migrate`
   - Start server: `python PCG_APP/manage.py runserver`

Visit http://127.0.0.1:8000/ to see the homepage.

## Development notes
- Templates in `PCG_APP/templates`.
- Static files at `PCG_APP/static` (compiled CSS outputs to `css/styles.css`).
- Add your apps to `INSTALLED_APPS` in `PCG_APP/PCG_APP/settings.py`.
- For production, configure environment variables (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL) and static files (collectstatic, whitenoise).
