# Auth Service

> For system context see: `docs/PROJECT.md`

## Responsibility
Handles user registration, authentication via email/password, and JWT issuance/validation.

## Entry Point
`python/src/auth/server.py` — Flask app, single file service.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | None | Creates a new user, returns 201 |
| POST | `/login` | HTTP Basic | Validates credentials, returns JWT |
| POST | `/validate` | Bearer JWT | Verifies JWT, returns decoded payload |

### POST /register
- **Input:** `Content-Type: application/json` — `{ "email": "...", "password": "..." }`
- **Success:** `201` — `{ "message": "user registered" }`
- **Failures:**
  - `400` — missing/empty fields
  - `409` — email already registered

### POST /login
- **Input:** HTTP Basic Auth header (`username=email`, `password=plaintext`)
- **Success:** `200` — JWT string
- **Failures:**
  - `401` — missing credentials or wrong password

### POST /validate
- **Input:** `Authorization: Bearer <jwt>` header
- **Success:** `200` — decoded JWT payload `{ "email", "authz", "exp" }`
- **Failures:**
  - `401` — missing token, wrong format, expired, or invalid

All error responses are JSON: `{ "error": "<code>", "detail": "<message>" }`.

## Password Hashing
Passwords are hashed with `bcrypt` (cost factor 12) before storage. `/login` uses `bcrypt.checkpw` to verify.

## JWT
- Algorithm: `HS256`
- Expiry: 1 day from issue
- Payload: `{ "email", "authz": true, "exp" }`
- Secret: `JWT_SECRET` env var

## DB Query Logic

### register
1. Validate JSON body
2. `bcrypt.hashpw(password)`
3. `INSERT INTO user (email, password) VALUES (%s, %s)`
4. Return 201 or 409 on `IntegrityError`

### login
1. Receive Basic Auth credentials
2. `SELECT email, password FROM user WHERE email=%s`
3. `bcrypt.checkpw(provided_password, stored_hash)`
4. On match → call `createJWT()`

## Database
- Engine: MySQL
- Schema: `auth`
- Table: `user(id INT PK, email VARCHAR UNIQUE, password VARCHAR)`
- Init script: `init.sql` (creates user, DB, table, seed row with bcrypt password)

## Environment Variables

| Var | Description |
|-----|-------------|
| `MYSQL_HOST` | DB host |
| `MYSQL_USER` | DB user |
| `MYSQL_PASSWORD` | DB password |
| `MYSQL_DB` | DB name (`auth`) |
| `MYSQL_PORT` | DB port (default 3306) |
| `JWT_SECRET` | Secret for signing JWT |
| `PORT` | Flask listen port (default 5000) |

## Dependencies
`Flask 3.1.3`, `PyMySQL 1.1.1`, `PyJWT 2.11.0`, `cryptography 44.0.2`, `bcrypt 4.2.1`
Tracked in `requirements.txt`.

## TODO

### Security
- [x] Hash passwords with `bcrypt`
- [ ] Add rate limiting on `/login` and `/register` to prevent brute force (Week 2)
- [ ] Rotate `JWT_SECRET` strategy — currently single static secret

### Endpoints
- [x] `POST /validate` — verify a JWT, return payload
- [x] `POST /register` — create a new user
- [ ] `POST /logout` — invalidate a token via Redis blacklist

### Reliability
- [ ] Connection pooling for MySQL — currently opens a new connection per request (Week 2)
- [x] Graceful JSON error responses on all endpoints

### Migrations
- [ ] Replace `init.sql` with Alembic migrations (Week 2)
