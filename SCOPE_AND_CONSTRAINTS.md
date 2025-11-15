# Campus Resource Hub – Scope & Constraints (v3)

## 1. Tech Stack (MUST)
- Language: Python 3
- Framework: Flask
- Rendering: Jinja2 templates with Bootstrap 5
- Database: SQLite (local file)
- Architecture: Single monolithic app with:
  - /src/app.py, /src/config.py
  - /src/controllers (Flask blueprints)
  - /src/models (ORM models)
  - /src/data_access (DB helpers)
  - /src/services (business logic)
  - /src/views (Jinja templates)
  - /src/static (CSS, JS, images)

## 2. Reference Implementation
- The folder `/reference/aidd-capstone-main/` is a **reference implementation**.
- Codex may:
  - Reuse the **architecture pattern**,
  - Reuse **naming ideas and routing structure**,
  - Align with the **same set of features**,
  - BUT must NOT copy code verbatim.
- Our implementation must be our own code in `/src/`, with:
  - Different layout structure (nav placement, card layout),
  - Different text/copy where reasonable,
  - Different visual arrangement (while still using Bootstrap).

## 3. Features – IN SCOPE (from AiDD brief + reference app)
- User auth:
  - Register, login, logout
  - Roles: student, staff, admin
- Resources:
  - Create, read, update, delete resources
  - Categories, basic search, and simple filters
  - Show availability and status
- Bookings:
  - Request bookings for a resource
  - Conflict detection (avoid overlapping bookings)
  - Status flow (pending, approved, rejected, cancelled)
- Messaging:
  - Basic message threads between requester and resource owner
- Reviews:
  - Rating + comment after a completed booking
- Admin:
  - Simple screens/tables to manage users, resources, bookings, and moderate reviews
- AI Feature:
  - ONE small “Resource Concierge” feature as required by the AiDD brief (e.g., suggest resources or summarize usage)
  - No additional AI complexity beyond this.

## 4. Explicitly OUT OF SCOPE
- React, Vite, Vue, Next.js, or any SPA front-end.
- Microservices, separate backend/front-end repos, or event-driven architectures.
- Additional features beyond those present in the AiDD brief and the reference app.
- Complex analytics dashboards, external email integrations, SSO/OAuth providers, or third-party APIs.
- Full redesign of business logic to be “more enterprise” than the reference.

## 5. Design Constraints
- Use Bootstrap 5, but:
  - Nav structure, layout, and UI composition **must differ** from `/reference/aidd-capstone-main/`.
  - Text labels and copy should be rephrased where reasonable.
  - It should be clearly a different implementation if both UIs are viewed side-by-side.

## 6. Testing & Documentation (Minimum)
- A few pytest tests covering:
  - At least one auth flow
  - Booking conflict detection
- README with setup and run instructions.
- Basic dev_notes in `.prompt/dev_notes.md` describing how AI was used.

## Code Reuse Policy

- Reference projects:
  - `/reference/aidd-capstone-main/` – full AiDD reference implementation (behavior & layouts).
  - `/reference/ui-admin-panel/` – UI / color / typography reference (design language).

- It is acceptable to:
  - Copy and adapt HTML/CSS/JS snippets from these reference projects,
  - Copy and adapt design tokens (colors, spacing, typography),
  - Mirror layout patterns and component structures.

- It is NOT acceptable to:
  - Break existing Flask routes or rename endpoints.
  - Break or rename Jinja variables, blocks, or form field names used by controllers.
  - Introduce new frameworks (React, Vite, etc.).
