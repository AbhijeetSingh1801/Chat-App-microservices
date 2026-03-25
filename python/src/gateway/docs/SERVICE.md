# Gateway Service

> For system context see: `docs/PROJECT.md`

## Responsibility
Single entry point for all client requests. Validates JWTs by calling the auth service, injects `X-User-Email` into downstream requests, and reverse-proxies to the correct service.

## Entry Point
`python/src/gateway/main.py` — FastAPI app, single file service.

## Request Flow

```
Client
  │  Authorization: Bearer <jwt>
  ▼
Gateway middleware
  │  POST /validate → Auth Service
  │  (401 if invalid)
  ▼ injects X-User-Email
  ├──► /auth/*      → Auth Service   (no X-User-Email injected)
  ├──► /user/*      → User Service
  ├──► /chat/*      → Chat Service
  ├──► /media/*     → Media Service
  ├──► /ws/*        → WebSocket Service
  └──► /presence/*  → Presence Service
```

## Public Paths (no JWT required)
| Path | Reason |
|------|--------|
| `GET /health` | Liveness probe |
| `POST /auth/login` | Unauthenticated by design |
| `POST /auth/register` | Unauthenticated by design |

## Routing Table
| Prefix | Downstream | Env var |
|--------|------------|---------|
| `/auth` | Auth Service | `AUTH_SERVICE_URL` |
| `/user` | User Service | `USER_SERVICE_URL` |
| `/chat` | Chat Service | `CHAT_SERVICE_URL` |
| `/media` | Media Service | `MEDIA_SERVICE_URL` |
| `/ws` | WebSocket Service | `WS_SERVICE_URL` |
| `/presence` | Presence Service | `PRESENCE_SERVICE_URL` |

## Headers
| Header | Direction | Description |
|--------|-----------|-------------|
| `Authorization: Bearer <jwt>` | Client → Gateway | Token for validation |
| `X-User-Email` | Gateway → Downstream | Decoded email, injected after validation |

Downstream services trust `X-User-Email` — they never verify JWTs themselves.

## Environment Variables
| Var | Default | Description |
|-----|---------|-------------|
| `AUTH_SERVICE_URL` | `http://auth:5000` | Auth service base URL |
| `USER_SERVICE_URL` | `http://user:8080` | User service base URL |
| `CHAT_SERVICE_URL` | `http://chat:8080` | Chat service base URL |
| `MEDIA_SERVICE_URL` | `http://media:8080` | Media service base URL |
| `WS_SERVICE_URL` | `http://websocket:8000` | WebSocket service base URL |
| `PRESENCE_SERVICE_URL` | `http://presence:5001` | Presence service base URL |

## Dependencies
`fastapi`, `uvicorn`, `httpx`
Tracked in `requirements.txt`.

## TODO
- [ ] Timeouts on upstream `httpx` calls
- [ ] Request ID header (`X-Request-ID`) propagation for tracing
- [ ] Rate limiting on public endpoints
