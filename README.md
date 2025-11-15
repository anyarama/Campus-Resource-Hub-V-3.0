# Campus Resource Hub v3

Server-rendered Flask application for the AiDD 2025 Campus Resource Hub project. This version now includes bookings, messaging, reviews, notifications, and an admin dashboard per Phase 2 scope.

## Stack
- Python 3 + Flask / Flask-Login / Flask-WTF
- SQLite for local persistence (stored under `instance/`)
- Jinja + Bootstrap 5 + custom CSS (no React/Vite per constraints)

## Getting started
1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` if you want to override defaults such as `SECRET_KEY` or `ALLOWED_EMAIL_DOMAINS`.
3. Initialize the database (drops existing data when `--force` is not used):
   ```bash
   flask --app src.app:create_app init-db
   ```
4. Run the development server:
   ```bash
   flask run
   ```
5. Sign in with any of the seeded accounts:
   - `admin@campus.test` / `AdminPass1!`
   - `staff@campus.test` / `StaffPass1!`
   - `student@campus.test` / `StudentPass1!`

## Tests
Run pytest with the default configuration:
```bash
pytest
```

## Repository layout
```
src/
  app.py              # Flask app factory + CLI command
  config.py           # Config objects
  controllers/        # Blueprints for site/auth/resources/dashboard
  data_access/        # SQLite helpers, DAL modules, and seed data
  templates/          # Jinja pages with sidebar-first layout
  static/             # Bootstrap overrides, JS, and uploads
.docs/context/        # Placeholder for PRD/personas per AiDD doc
.prompt/              # AI usage log per course policy
```

Phase 3 will focus on the concierge AI endpoint, deeper testing, and final polish.
