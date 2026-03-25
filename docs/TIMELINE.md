
# Project Timeline — WhatsApp Clone

> Assumes part-time work (~2–3 hrs/day).
> Each phase ends with a working, Dockerized, documented service.
> Dates are from project start: **2026-03-25**

---

## Phase 1 — Auth Complete + Gateway
**Duration: 2 weeks | 2026-03-25 → 2026-04-08**

### Week 1 (Mar 25 – Mar 31) — Auth Core + Gateway
| Day | Task | Status |
|-----|------|--------|
| 1 | `POST /login` — validate credentials, return JWT | ✅ done |
| 1 | `POST /validate` — verify JWT, return payload | ✅ done |
| 1 | Gateway — FastAPI setup, middleware, reverse proxy, Dockerfile | ✅ done |
| 2 | `POST /register` — create user, bcrypt password hashing | ← now |
| 2 | JSON error responses in auth | ← now |
| 3 | Gateway `.env` + root `docker-compose.yml` (auth + gateway together) | ← now |
| 4–5 | Manual end-to-end test: register → login → gateway protected route | |
| 6–7 | Update auth + gateway `SERVICE.md`, close TODOs | |

**Deliverable:** Auth (login + validate + register) + Gateway running end-to-end.

### Week 2 (Apr 1 – Apr 8) — Hardening + Alembic
| Day | Task |
|-----|------|
| 1–2 | Replace `init.sql` → Alembic migration setup |
| 3–4 | MySQL connection pooling in auth |
| 5–6 | Rate limiting on `/login` + `/register` |
| 7 | Close all remaining auth TODOs, final `SERVICE.md` pass |

**Deliverable:** Auth fully hardened with Alembic migrations and production-safe security.

---

## Phase 2 — User + Chat Services (Java)
**Duration: 3 weeks | 2026-04-09 → 2026-04-29**

### Week 3 (Apr 9 – Apr 15) — User Service
| Day | Task |
|-----|------|
| 1   | Spring Boot project setup, Dockerfile |
| 2–3 | `GET/PUT /profile` — view and update user profile |
| 4–5 | `POST /contacts` + `GET /contacts` — contact list |
| 6   | Flyway migration setup, replace `schema.sql` |
| 7   | Docs + `SERVICE.md` |

**Deliverable:** User profiles and contacts over REST.

### Week 4–5 (Apr 16 – Apr 29) — Chat Service
| Day | Task |
|-----|------|
| 1–2 | Spring Boot setup, Dockerfile, MySQL schema |
| 3–4 | `POST /messages` — send a message (stored in MySQL) |
| 5–6 | `GET /messages/{conversationId}` — fetch history with pagination |
| 7–8 | Redis integration — unread counts + recent message cache |
| 9–10 | `PATCH /messages/{id}/status` — update `sent/delivered/read` |
| 11–12 | RabbitMQ publish — emit event when recipient is offline |
| 13–14 | Flyway migrations, docs, `SERVICE.md` |

**Deliverable:** Full message send/receive/history with status tracking.

---

## Phase 3 — Real-Time Layer
**Duration: 2 weeks | 2026-04-30 → 2026-05-13**

### Week 6 (Apr 30 – May 6) — Presence Service
| Day | Task |
|-----|------|
| 1–2 | Flask setup, Redis client |
| 3–4 | `POST /heartbeat` — refresh TTL key per user |
| 5   | `GET /presence/{userId}` — return online/offline + last seen |
| 6–7 | Docs + wire into gateway routing |

**Deliverable:** Online/offline status with automatic TTL expiry.

### Week 7 (May 7 – May 13) — WebSocket Service
| Day | Task |
|-----|------|
| 1–2 | FastAPI + WebSocket setup, Dockerfile |
| 3–4 | Connection registry in Redis — `user_id → node mapping` |
| 5–6 | Redis Pub-Sub — fan-out messages to correct WS node |
| 7   | Handle reconnect, missed messages on reconnect |

**Deliverable:** Real-time message delivery between two connected clients.

---

## Phase 4 — Media + Notifications
**Duration: 3 weeks | 2026-05-14 → 2026-06-03**

### Week 8–9 (May 14 – May 27) — Media Service
| Day | Task |
|-----|------|
| 1–2 | Spring Boot setup, S3 bucket config (boto equiv: AWS SDK v2) |
| 3–4 | `POST /upload` — stream file to S3, store metadata in MySQL |
| 5–6 | `GET /media/{id}` — return pre-signed S3 URL |
| 7–8 | RabbitMQ job publish — trigger async thumbnail generation |
| 9–10 | RabbitMQ consumer (worker) — generate thumbnail, update metadata |
| 11–14 | Flyway migrations, docs, `SERVICE.md` |

**Deliverable:** File upload/download via S3, async thumbnail processing.

### Week 10 (May 28 – Jun 3) — Notification Service
| Day | Task |
|-----|------|
| 1–2 | Python RabbitMQ consumer setup |
| 3–4 | Firebase Admin SDK — send FCM push to device token |
| 5   | Store device tokens in user service DB |
| 6–7 | Retry logic for failed pushes, dead-letter queue |

**Deliverable:** Push notification sent when message recipient is offline.

---

## Phase 5 — Infrastructure
**Duration: 4 weeks | 2026-06-04 → 2026-07-01**

### Week 11 (Jun 4 – Jun 10) — Terraform
| Day | Task |
|-----|------|
| 1–2 | Terraform project setup, remote state in S3 + DynamoDB lock |
| 3–4 | EKS cluster module |
| 5   | RDS (MySQL) + ElastiCache (Redis) modules |
| 6   | S3 bucket + Amazon MQ (RabbitMQ) modules |
| 7   | Secrets Manager entries, IAM roles |

**Deliverable:** Full AWS infra provisionable with `terraform apply`.

### Week 12 (Jun 11 – Jun 17) — Helm Charts
| Day | Task |
|-----|------|
| 1–2 | Helm chart structure + base template |
| 3–5 | Chart per service (auth, gateway, user, chat, websocket, presence, media, notification) |
| 6–7 | Values files per environment (`dev.yaml`, `prod.yaml`) |

**Deliverable:** Every service deployable to K8s with `helm install`.

### Week 13 (Jun 18 – Jun 24) — ArgoCD + GitOps
| Day | Task |
|-----|------|
| 1–2 | ArgoCD install on EKS |
| 3–4 | ArgoCD `Application` manifests per service |
| 5–6 | Auto-sync on `main` branch merge |
| 7   | Rollback test — `git revert` → ArgoCD re-syncs |

**Deliverable:** Push to `main` → services auto-deploy to EKS.

### Week 14 (Jun 25 – Jul 1) — GitHub Actions CI/CD
| Day | Task |
|-----|------|
| 1–2 | `build-python.yml` — lint + test + Docker build + ECR push |
| 3–4 | `build-java.yml` — Maven build + test + Docker build + ECR push |
| 5–6 | `infra.yml` — `terraform plan` on PR, `terraform apply` on merge to main |
| 7   | End-to-end test: PR → CI → merge → ArgoCD deploy |

**Deliverable:** Full CI/CD pipeline live.

---

## Milestones Summary

| Milestone | Date | What works |
|-----------|------|------------|
| Auth complete | Apr 8 | Login, register, validate JWT |
| Core REST APIs | Apr 29 | User profiles, contacts, message send/receive |
| Real-time messaging | May 13 | WebSocket delivery, presence |
| Full feature set | Jun 3 | Media uploads, push notifications |
| Infra provisioned | Jun 10 | AWS EKS, RDS, Redis, S3 via Terraform |
| GitOps live | Jun 24 | ArgoCD auto-deploy on merge |
| CI/CD complete | Jul 1 | Full pipeline end-to-end |

---

## TODOs Across All Phases
- [ ] Shared `docker-compose.yml` at root (all services local)
- [ ] Centralized logging — ELK or CloudWatch
- [ ] External Secrets Operator (K8s ↔ AWS Secrets Manager)
- [ ] API versioning strategy (`/v1/...`)
- [ ] Load testing before prod (k6 or Locust)
