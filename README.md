# Multi Wellness System - Local Server

This repository contains static HTML pages for the Multi Wellness System with MySQL backend.

## Prerequisites

Ensure MySQL is installed and running locally. Create the database:

```sql
CREATE DATABASE rohitproject;
```

## Quick local run (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python "app.py"
```

## Features

- The server listens on port 5000 by default.
- Root `/` serves `home2.html` if present, otherwise the first HTML file found.
- Any other `/*.html` file in the project root is served (e.g. `/login2.html`).
- The `/login` POST route stores login events in **MySQL** (`rohitproject.login_logs`) and redirects to `/success`.

## Database

- **Database**: rohitproject
- **Username**: root
- **Password**: root
- **Host**: localhost

The `login_logs` table is created automatically on first login attempt.
