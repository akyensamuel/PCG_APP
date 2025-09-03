#!/bin/bash

# Vercel build script for Django + Tailwind CSS project

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Node.js dependencies..."
npm install

echo "Building Tailwind CSS..."
npm run tailwind:build

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!"
