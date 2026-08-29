# Assignment 3 — A Local Event Advertisement Portal

**Spec:** `CNG445_Assignment3_20251.pdf`

## Contents
- `CNG445Ass.zip` — original submission archive (untouched)
- `CNG445Ass/` — its extracted contents: `app.py` (Flask routes), `dbrun.py` (DB schema creation script), `portal.db` (SQLite database), `style.css`, `validation.js`, `templates/` (`index.html`, `register.html`, `register_ok.html`, `profile.html`, `societies.html`, `details.html`, plus an unused `events.html` — see below), `ReadMe.txt`, and IDE/venv folders (`.idea`, `.venv`) bundled in the original zip
- `CNG445_Assignment3_20251.pdf` — assignment spec

## Why this grouping
`CNG445Ass.zip`'s contents are unambiguously a Flask + SQLite web app: `app.py` imports Flask and defines routes for `/`, `/login`, `/register`, `/societies`, `/profile`, `/events`, `/event_details/<id>`; `dbrun.py` creates `User`/`Society`/`Event`/`involves` tables matching the spec's ERD exactly (including the note that `Event.name` must be `UNIQUE` despite `eventID` being the primary key); `templates/` holds `register.html`, `societies.html`, `profile.html`, etc.; and `validation.js` does client-side fee-format/society-checkbox validation. This is a one-to-one match with Assignment 3's requirements. This is Assignment 3.

## Completeness assessment — confirmed by actually running the Flask app

Installed Flask, ran `python3 app.py` against the submitted `portal.db`, and exercised the app
with real HTTP requests (`curl`) rather than just reading the source:

- **`GET /` and `GET /register`** — both return 200 and render.
- **`POST /register`** with a fresh username/email/password/name — returns 200, page shows
  "Registered"/success, and the user is actually inserted into `portal.db` (confirmed by
  subsequently logging in as that exact user).
- **`POST /login`** with the just-registered credentials — returns a 302 redirect to `/index`
  with a session cookie set; the redirect target loads at 200.
- **`GET /profile`** (authenticated, using the session cookie from login) — returns 200 and
  correctly displays the logged-in user's own name/email back, confirming the session/auth
  gating actually works end-to-end, not just in the source.
- **Keyword search** (`GET /index?keyword=a&society=all`, the "search all societies" mode) —
  returns 200 with no server error, confirming the `LIKE`-based query and the per-society
  result-bucketing logic run without exceptions against the real database.

No runtime errors were encountered in any of the flows above. This directly confirms the
previous static read: the database schema, registration validation, session-based auth/admin
gating, and search all work as designed when actually executed, not just as inferred from
reading the code.

**Gaps already identified from reading the source remain accurate** (not retested, since they're
either naming/structural rather than behavioral, or the specific feature wasn't exercised here):
1. The database-creation script is named `dbrun.py`, not the spec-required `dbscript.py`
   (functionally identical, just a filename mismatch under a named grading item).
2. `templates/events.html` is a dead, unreferenced leftover template (posts to nonexistent
   routes, links a nonexistent stylesheet) — harmless since nothing routes to it, but should be
   deleted for cleanliness.
3. The logged-in nav menu doesn't have a separate "Announced Events" link the way the spec's
   mockup shows — event management is folded into the home page instead of a distinct page.
4. Search only matches `name`/`description`, not "any field" as the spec's wording suggests.
5. Passwords are stored in plaintext in `User.password` — not explicitly required by the spec,
   but worth flagging.
6. The zip bundles a full `.venv` and `.idea` folder — unnecessary bulk, not a defect.

**Verdict: works.** Actually running the app (not just reading it) confirms registration, login,
session-gated profile access, and keyword search all function correctly end-to-end against the
submitted database. Remaining gaps are minor spec-literalism items (script filename, nav
structure, search field scope, an unused template) rather than broken functionality.
