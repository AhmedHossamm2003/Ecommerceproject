# Phase 1 Environment Validation

**Workstation validation date:** 19 November 2026  
**Scope:** Docker Compose, PostgreSQL, pgAdmin, networking, browser access, and persistent storage  
**Overall result:** PASSED

## Validated components

| Component | Observed result | Status |
|---|---|---|
| Docker Desktop | Version 4.99.0 | Passed |
| Docker Engine and CLI | Version 29.9.3 | Passed |
| WSL | Version 3.0.1; Docker distribution running as WSL 2 | Passed |
| Docker Compose model | `docker compose config` resolved successfully | Passed |
| PostgreSQL | `postgres:17.12-alpine3.23`; container healthy | Passed |
| pgAdmin | `dpage/pgadmin4:9.19.0`; container healthy | Passed |
| pgAdmin HTTP | `http://localhost:5050/misc/ping` returned `200 PING` | Passed |
| Persistent storage | Both named volumes use Docker's local driver | Passed |

## Commands and observed evidence

The following commands were executed from the repository root:

```powershell
docker compose config
docker compose up -d
docker compose ps
docker compose exec -T postgres pg_isready -U ecommerce_user -d ecommerce_db
docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db -c "SELECT current_database(), current_user, version();"
docker volume inspect ecommerce_postgres_data ecommerce_pgadmin_data
```

Observed results:

- PostgreSQL reported `/run/postgresql:5432 - accepting connections`.
- The database query returned `ecommerce_db`, `ecommerce_user`, and PostgreSQL 17.12.
- The `ecommerce_db` database was found in `pg_database`.
- `ecommerce_postgres_data` and `ecommerce_pgadmin_data` both use the `local` volume driver.
- The pgAdmin container resolved service host `postgres` and reached port 5432.
- The pgAdmin container authenticated to PostgreSQL and returned (`ecommerce_db`, `ecommerce_user`).
- pgAdmin's internal database contains the predefined server **E-commerce PostgreSQL (Docker)** with host `postgres`, port 5432, maintenance database `ecommerce_db`, and username `ecommerce_user`.

## Browser validation

The browser interface was actually tested at `http://localhost:5050`:

1. The pgAdmin login page loaded.
2. The configured development login succeeded.
3. Object Explorer showed one predefined server.
4. The PostgreSQL password was entered without saving it in the repository or browser.
5. pgAdmin displayed **Server connected** and loaded the server dashboard.

An unrelated pgAdmin update-check notification (`urlopen ... Try again`) appeared because outbound update access was unavailable; it did not affect the local database connection or dashboard.

## Persistence and security interpretation

Normal `docker compose down` removes containers and the project network but preserves both named volumes. `docker compose down --volumes` was deliberately not executed because it would erase local PostgreSQL and pgAdmin state. The environment used only the safe development defaults for validation. New clones should copy `.env.example` to `.env` and choose passwords before first startup. On this already-initialized workstation, changing `.env` alone will not rewrite stored credentials; keep the validation defaults for the recording or deliberately update/reset the local state using the README guidance. `.env` and raw source files are excluded from Git.
