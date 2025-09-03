# PCG - A.N.T (Django)

A church platform built with Django. This repo includes Tailwind CSS for styling.

## Quickstart

1. **Environment Setup**
   - Copy environment file: `cp .env.example .env`
   - Update `.env` with your configuration (see ENVIRONMENT_SETUP.md for details)

2. **Python Environment**
   - Create/activate a venv (Windows): `virtual\Scripts\activate` or your preferred venv name
   - Install deps: `pip install -r requirements.txt`

3. **Node (for Tailwind)**
   - Install Node 18+ and run: `npm install`
   - Build CSS once: `npm run tailwind:build`
   - Or watch: `npm run tailwind:watch`

4. **Django**
   - Run migrations: `python manage.py migrate`
   - Start server: `python manage.py runserver`

Visit http://127.0.0.1:8000/ to see the homepage.

## Configuration

This project uses environment variables for configuration management:
- **Development**: Uses `.env` file (not committed to git)
- **Production**: Set environment variables directly on your server
- See `ENVIRONMENT_SETUP.md` for detailed configuration instructions
- Example configuration available in `.env.example`

## Development Notes
- Templates in app directories under `templates/`
- Static files at `static/` (compiled CSS outputs to `css/styles.css`)
- Add your apps to `INSTALLED_APPS` in `PCG_APP/settings.py`
- Environment variables are managed via python-decouple
- For production, configure all environment variables and run `python manage.py collectstatic`
