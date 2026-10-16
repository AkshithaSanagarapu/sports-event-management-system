# Sports Event Management System

A college sports event management project built with **Flask**, **MongoDB**, and server-rendered HTML templates. It includes separate interfaces for students, event organizers, and administrators, plus an experimental Flutter WebView client.

## Features

The codebase includes:

- Student registration and login
- Event organizer login and event management screens
- Event listings, search, and registration flows
- Student notifications, invoices, and complaints
- Ground and organization proposal forms
- Administrator views for organizers and requests
- Optional email delivery for organizer credentials (requires SMTP configuration)

**Testing status:** The Flask homepage, student signup, student login, and student dashboard have been exercised locally with MongoDB. Other workflows are present in the source but have not been fully verified end-to-end.

## Tech stack

- **Backend:** Python, Flask, PyMongo, bcrypt
- **Database:** MongoDB
- **Frontend:** HTML, CSS, JavaScript, Jinja templates
- **Optional mobile client:** Flutter/Dart WebView in `new_deisgn/app`

## Run locally (macOS / Linux)

### Prerequisites

- Python 3.9 or newer
- MongoDB Community Server running locally on port `27017`

On macOS, MongoDB can be installed with Homebrew:

```bash
brew tap mongodb/brew
brew install mongodb-community@8.0
brew services start mongodb-community@8.0
```

Homebrew may require you to explicitly trust MongoDB's official tap before installation (`brew trust mongodb/brew`).

### Start the Flask app

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --port 5001
```

Open **http://127.0.0.1:5001** in your browser.

On Windows, activate the virtual environment using `.venv\Scripts\activate` instead.

The app defaults to `mongodb://localhost:27017/` and uses a database named `sportsmanagement`. You can override the connection string with the `MONGODB_URI` environment variable.

### Optional configuration

See `.env.example` for available environment variables:

- `MONGODB_URI`: MongoDB connection string
- `FLASK_SECRET_KEY`: persistent Flask session signing key
- `ADMIN_PASSWORD`: demo administrator password
- `SMTP_EMAIL` and `SMTP_APP_PASSWORD`: optional Gmail SMTP credentials for organizer emails

**Note:** `app.py` reads environment variables directly; it does not automatically load `.env`. Set the variables in your shell or use an environment loader before starting Flask. Never commit `.env` or actual credentials.

### Optional Flutter client

The `new_deisgn/app` directory contains a Flutter WebView wrapper. Its WebView address may need to be adjusted for your emulator/device and the Flask port. The mobile flow has not been verified in the current cleanup.

## Project structure

```text
app.py                Flask routes and MongoDB integration
templates/            Server-rendered HTML views
new_deisgn/app/       Optional Flutter WebView project
uploads/              Runtime upload directory (contents ignored by Git)
requirements.txt      Python dependencies
.env.example          Example environment variable names
```

## Current limitations

This is a **local-development / academic project**, not a production-ready service. The code needs further work on role-based access checks, administrator authentication, session security, input validation, and automated tests. Do not expose the Flask development server publicly or use real personal data without addressing these issues.

## Notes

This repository contains no screenshots. The `userrequirements.txt` file from the original project was a feature outline rather than a valid Python dependency list; use `requirements.txt` to install dependencies.
