# DevPulse

A personal developer dashboard that aggregates contest data from Codeforces,
LeetCode and CodeChef, and gives you one place to track goals, projects, and
activity instead of monitoring each platform separately.

## Stack

- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL, httpx
- **Frontend:** React (Vite), Tailwind CSS, React Router, axios

## How the requirements map to the code

| Requirement | Where it lives |
|---|---|
| 1. Concurrent aggregation from Codeforces/LeetCode/CodeChef | `backend/app/services/contest_providers/*.py` (one adapter per platform) + `backend/app/services/aggregator.py` (fetches all three with `asyncio.gather`) |
| 2. Normalize + cache so the frontend isn't hitting external services constantly | `ContestOut` schema normalizes every platform's response; `backend/app/services/cache.py` is a lock-guarded TTL cache (10 min default) |
| 3. Persist accounts, profiles, bookmarks, goals, projects, activity in PostgreSQL | `backend/app/models/*.py`, all via SQLAlchemy against Postgres |
| 4. Track contests participated in, learning progress, projects, activity | `ActivityLog` model + `/api/activity` routes; `github` is a supported `ActivityType` for when GitHub sync is added |
| 5. One unified dashboard instead of per-platform monitoring | `GET /api/dashboard` assembles contests + goals + projects + activity + stats in a single response; `frontend/src/pages/Dashboard.jsx` renders it |
| 6. Goals tied to progress tracking | `Goal` model (title, category, status, 0-100 progress, target date) + `/api/goals` CRUD + the progress slider in `Goals.jsx` |
| Personalized login (Google / Microsoft) | `backend/app/core/oauth.py` (authorization-code flow for both providers) + `/api/auth/{provider}/login` and `/callback` routes; frontend `OAuthCallback.jsx` + buttons on `Login.jsx`/`Register.jsx` |
| Handle sync — live rating/rank/solved-count per linked platform | `backend/app/services/platform_stats.py` (concurrent fetch, per-user TTL cache) + `GET /api/profile/stats`; `Profile.jsx` fetches on load and force-refreshes right after you hit "Save & sync" |
| 7. Personalized insights (gaps, recommendations) | Not built yet — see "Where to go next" below. The data model already supports it: goals + activity + projects + synced platform stats are all in one Postgres DB, ready for a recommendation query or model. |

## Project layout

```
devpulse/
  backend/
    app/
      core/           # settings, JWT/password hashing
      db/              # SQLAlchemy engine/session
      models/          # User, Bookmark, Goal, Project, ActivityLog
      schemas/         # Pydantic request/response shapes
      services/
        contest_providers/   # one adapter per platform
        aggregator.py         # concurrent fetch + merge
        cache.py              # TTL cache
      api/routes/       # auth, profile, contests, goals, projects, activity, dashboard
      main.py
    requirements.txt
    .env.example
  frontend/
    src/
      api/             # axios client with auth interceptor
      context/         # AuthContext
      components/      # Layout, StatTile, ContestRow
      pages/           # Login, Register, Dashboard, Contests, Goals, Projects, Profile
    .env.example
```

## Running it locally

### 1. Database

You need a PostgreSQL instance. Locally:

```bash
createdb devpulse
```

Or point `DATABASE_URL` at any Postgres instance (RDS, Supabase, Railway, etc).

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL / SECRET_KEY as needed
uvicorn app.main:app --reload
```

Tables are created automatically on startup (`Base.metadata.create_all`).
For real schema migrations later, swap this for Alembic.

API docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE, defaults to localhost:8000
npm run dev
```

App: `http://localhost:5173`

## Upgrading an existing install (if you set this up before OAuth/handle-sync were added)

The `users` table changed: `hashed_password` is now nullable (OAuth accounts
don't have one) and there's a new `oauth_provider` column. Run this once
against your existing database:

```sql
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50);
```

(`Base.metadata.create_all` only creates tables that don't exist yet — it
won't alter a table that's already there, which is why this needs a manual
`ALTER TABLE` once. A fresh `createdb` doesn't need this; the model already
reflects it.)

## Setting up Google / Microsoft login

Both are optional — if you don't configure them, the "Continue with
Google/Microsoft" buttons will just redirect to an error, and normal
email/password login still works fine. To turn them on:

**Google:**
1. Go to https://console.cloud.google.com/apis/credentials
2. Create an OAuth 2.0 Client ID (type: Web application)
3. Add `http://localhost:8000/api/auth/google/callback` as an authorized redirect URI
4. Put the client ID/secret into `backend/.env` as `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`

**Microsoft:**
1. Go to https://portal.azure.com → Microsoft Entra ID → App registrations → New registration
2. Set the redirect URI (platform: Web) to `http://localhost:8000/api/auth/microsoft/callback`
3. Under "Certificates & secrets", create a client secret
4. Put the client ID/secret into `backend/.env` as `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`

Restart the backend after adding either. A user who signs up via OAuth and
one who registers with the same email/password are treated as the same
account (matched by email) — signing in with either method afterward works.

## A note on the contest and stats providers

- **Codeforces** uses their official public API for both contest listings
  and user stats (`user.info`) — stable and documented.
- **LeetCode** and **CodeChef** have no official public APIs for contests
  *or* user profiles. The adapters use the same unofficial endpoints their
  own websites call, and the CodeChef stats fetcher scrapes a rating value
  out of the profile page's embedded JSON. These can change without notice
  or block requests that look automated. Every provider fails independently
  and returns an error string instead of raising, so one platform being
  unreachable or one handle being misspelled never breaks the others or
  the dashboard.
- I built and tested this from a sandboxed environment without open
  internet access to those three domains, so I verified against real
  PostgreSQL end-to-end (auth including the OAuth code paths, goals,
  projects, activity, dashboard aggregation, and the stats-sync endpoint
  all work against a live database and construct correct requests) but
  could not verify a live, successful external fetch. Run it from your
  own machine to see real contest and stats data — the request/response
  handling is complete and this is just a network-reachability limitation
  of my sandbox.

## Where to go next

- **GitHub activity sync**: `github_username` is already captured on the
  profile and `ActivityType.github` already exists — add a provider that
  hits the GitHub REST/GraphQL API for commits/PRs and logs them as
  `ActivityLog` rows on a schedule.
- **Personalized insights**: with goal progress, activity history, and
  synced platform stats all in one place now, a reasonable v1 is a
  scheduled job that flags gaps, e.g. "no DSA activity in 2 weeks but your
  'Improve DSA' goal is still in progress" or "your Codeforces rating
  hasn't moved in a month." That's a SQL query and a rules engine before
  it needs to be anything fancier.
- **Background refresh**: right now both the contest cache and the
  per-user stats cache refresh lazily (on the first request after they go
  stale). For a snappier first load, add an `asyncio` background task on
  startup that refreshes the contest cache proactively.
- **OAuth hardening**: the current flow skips verifying the `state`
  parameter round-trips (CSRF protection) to keep the MVP simple — worth
  adding before this goes anywhere near production, e.g. storing `state`
  in a short-lived server-side cache or a signed cookie and checking it
  in the callback.
- **Alembic migrations**: swap `Base.metadata.create_all` for real
  migrations before this touches a production database with existing data.
