# Auth Service

> For system context see: `docs/PROJECT.md`
> For module details see: `docs/modules/<module>.md`

## Responsibility
Authenticates users via email/password and issues signed JWT tokens.

## Entry Point
`python/src/auth/server.py` — Flask app, single file service.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/login` | HTTP Basic | Validates credentials, returns JWT |
| POST | `/validate` | Bearer JWT | Verifies JWT, returns decoded payload |

### POST /login
- **Input:** HTTP Basic Auth header (`username=email`, `password`)
- **Success:** `200` — JWT string
- **Failures:** `401 missing credentials` / `401 invalid credentials`

## Modules

| Module | Location | Doc |
|--------|----------|-----|
| JWT creation | `server.py::createJWT()` | `docs/modules/jwt.md` |
| DB query | `server.py::login()` | inline in SERVICE.md (below) |

## DB Query Logic (login)
1. Receive Basic Auth credentials
2. `SELECT email, password FROM user WHERE email=%s`
3. Compare returned row against provided credentials (plaintext — see TODO)
4. On match → call `createJWT()`

## Database
- Engine: MySQL
- Schema: `auth`
- Table: `user(id INT PK, email VARCHAR UNIQUE, password VARCHAR)`
- Init script: `init.sql`

## Environment Variables

| Var | Description |
|-----|-------------|
| `MYSQL_HOST` | DB host |
| `MYSQL_USER` | DB user |
| `MYSQL_PASSWORD` | DB password |
| `MYSQL_DB` | DB name (`auth`) |
| `MYSQL_PORT` | DB port |
| `JWT_SECRET` | Secret for signing JWT |

## Dependencies
`Flask 3.1.3`, `PyMySQL 1.1.1`, `PyJWT 2.11.0`, `cryptography 44.0.2`
Tracked in `requirements.txt`. Venv at `python/src/auth/venv/`.

## TODO

### Security (do before prod)
- [ ] Hash passwords with `bcrypt` — currently stored plaintext in DB
- [ ] Add rate limiting on `/login` to prevent brute force
- [ ] Rotate `JWT_SECRET` strategy — currently single static secret

### Endpoints (core missing functionality)
- [x] `POST /validate` — verify a JWT, return payload; needed by all other services
- [ ] `POST /register` — create a new user; currently only possible via raw SQL
- [ ] `POST /logout` — invalidate a token via Redis blacklist

### Reliability
- [ ] Connection pooling for MySQL — currently opens a new connection per request
- [ ] Graceful error responses as JSON instead of plain strings

### Migrations
- [ ] Replace `init.sql` with Alembic migrations for schema versioning
