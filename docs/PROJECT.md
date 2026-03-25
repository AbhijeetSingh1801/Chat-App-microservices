# WhatsApp Clone — System Design Project

## Purpose
Microservice-based WhatsApp clone. Each service is independently deployable
with its own database. Goal is to learn real-world system design + DevOps patterns.

## Doc Navigation (read top-down, only what you need)
```
docs/PROJECT.md                              ← you are here (system map)
python/src/<service>/docs/SERVICE.md         ← Python service internals
java/src/<service>/docs/SERVICE.md           ← Java service internals
infrastructure/docs/INFRA.md                 ← Terraform + K8s + ArgoCD
```

---

## Repository Structure

```
/
├── python/src/
│   ├── auth/           Flask  — login, JWT
│   ├── gateway/        FastAPI — routing, JWT validation
│   ├── websocket/      FastAPI — real-time WS
│   ├── presence/       Flask  — online/offline (Redis)
│   └── notification/   Python worker — push via FCM
│
├── java/src/
│   ├── user/           Spring Boot — profiles, contacts
│   ├── chat/           Spring Boot — messages, history
│   └── media/          Spring Boot — uploads, S3
│
└── infrastructure/
    ├── terraform/       AWS infra (EKS, RDS, ElastiCache, S3, Secrets)
    ├── helm/            Helm charts per service
    ├── argocd/          ArgoCD app definitions (GitOps)
    └── k8s/             Base Kubernetes manifests
```

---

## Microservices

| Service      | Lang   | Path                      | Status  | Responsibility                          |
|--------------|--------|---------------------------|---------|-----------------------------------------|
| auth         | Python | python/src/auth/          | active  | Login, JWT issuance, token validation   |
| gateway      | Python | python/src/gateway/       | planned | Entry point, JWT check, routing         |
| websocket    | Python | python/src/websocket/     | planned | Real-time delivery via WebSocket        |
| presence     | Python | python/src/presence/      | planned | Online/offline status, last seen        |
| notification | Python | python/src/notification/  | planned | Push notifications (FCM) when offline   |
| user         | Java   | java/src/user/            | planned | Profiles, contacts, phone registration  |
| chat         | Java   | java/src/chat/            | planned | Store/retrieve messages, history        |
| media        | Java   | java/src/media/           | planned | Upload/serve images, video, documents   |

**Why Python for some, Java for others:**
- Python (Flask/FastAPI) — lightweight, async-first services (gateway, WS, presence)
- Java (Spring Boot) — heavier business logic, rich ecosystem (user, chat, media)

---

## Architecture Overview

```
Client
  │
  ▼
[API Gateway - FastAPI]  ← JWT validation, rate limiting
  │
  ├── REST ──► auth (Python) / user (Java) / chat (Java) / media (Java) / presence (Python)
  │
  └── WS ────► websocket (Python/FastAPI)
                   │
             Redis Pub-Sub  ←── fan-out across WS nodes
                   │
             RabbitMQ queue ─── notification worker (Python)
                                      │
                                   FCM push
```

---

## Inter-Service Communication

| Pattern        | Used for                                              |
|----------------|-------------------------------------------------------|
| REST (HTTP)    | Synchronous: login, fetch profile, upload media       |
| WebSocket      | Real-time message delivery to connected clients       |
| RabbitMQ       | Async: offline notifications, media processing jobs  |
| Redis Pub-Sub  | WS message fan-out across multiple nodes              |

---

## Shared Contracts

- **Auth token:** JWT (HS256), payload: `{ email, authz, exp }`
- **Protected routes:** `Authorization: Bearer <token>` header
- **Gateway** validates JWT → forwards `X-User-Email` to downstream services
- **Message schema:** `{ id, from, to, type, content, timestamp, status }`
- **Status flow:** `sent` → `delivered` → `read`

---

## Tech Stack — Per Service

### auth — Python/Flask
| Layer     | Choice |
|-----------|--------|
| Framework | Flask 3.x |
| DB        | MySQL |
| Auth      | PyJWT, bcrypt |

### gateway — Python/FastAPI
| Layer     | Choice |
|-----------|--------|
| Framework | FastAPI (async) |
| Proxy     | httpx (async reverse proxy) |
| Auth      | PyJWT — validates + injects headers |
| Why       | Async-first, handles high concurrency, auto OpenAPI docs |

### websocket — Python/FastAPI
| Layer     | Choice |
|-----------|--------|
| Framework | FastAPI + native WebSocket |
| Pub-Sub   | Redis — fan-out to all WS server nodes |
| Session   | Redis — maps `user_id → node` |
| Why       | Native async WS, scales horizontally with Redis |

### presence — Python/Flask
| Layer     | Choice |
|-----------|--------|
| Framework | Flask |
| Store     | Redis only (no SQL) |
| Pattern   | Key `presence:<user_id>` with TTL, heartbeat refreshes |
| Why       | Ephemeral data, TTL handles disconnect automatically |

### notification — Python worker
| Layer     | Choice |
|-----------|--------|
| Type      | RabbitMQ consumer (no HTTP server) |
| Push      | Firebase Admin SDK (FCM) |
| Why       | Pure consumer, no inbound traffic needed |

### user — Java/Spring Boot
| Layer     | Choice |
|-----------|--------|
| Framework | Spring Boot 3.x + Spring Web |
| DB        | MySQL + Spring Data JPA |
| Migration | Flyway |
| Why Java  | Rich validation, Spring Security integration, JPA relations |

### chat — Java/Spring Boot
| Layer     | Choice |
|-----------|--------|
| Framework | Spring Boot 3.x + Spring Web |
| DB        | MySQL (message history) |
| Cache     | Redis (recent messages, unread counts) |
| Queue     | Spring AMQP → RabbitMQ (publish offline events) |
| Migration | Flyway |

### media — Java/Spring Boot
| Layer     | Choice |
|-----------|--------|
| Framework | Spring Boot 3.x + Spring Web |
| Storage   | AWS S3 (AWS SDK v2) |
| Queue     | Spring AMQP → RabbitMQ (async processing jobs) |
| DB        | MySQL (file metadata) |
| Migration | Flyway |

---

## Infrastructure Stack

### Provisioning — Terraform
```
infrastructure/terraform/
├── modules/
│   ├── eks/          EKS cluster
│   ├── rds/          MySQL per service (or shared with separate schemas)
│   ├── elasticache/  Redis cluster
│   ├── s3/           Media bucket
│   ├── mq/           Amazon MQ (RabbitMQ)
│   └── secrets/      AWS Secrets Manager entries
└── environments/
    ├── dev/          tfvars for dev
    └── prod/         tfvars for prod
```

### Container Orchestration — Kubernetes (EKS)
- Each service → its own `Deployment` + `Service` + `HorizontalPodAutoscaler`
- Secrets injected from AWS Secrets Manager via **External Secrets Operator**
- Ingress via **AWS ALB Ingress Controller**

### Packaging — Helm
```
infrastructure/helm/
├── auth/
├── gateway/
├── user/
├── chat/
└── ...   ← one chart per service
```
Each chart parameterises image tag, replicas, env, resource limits.

### GitOps — ArgoCD
```
infrastructure/argocd/
└── apps/
    ├── auth-app.yaml
    ├── gateway-app.yaml
    └── ...
```
- ArgoCD watches the `main` branch
- Push to `main` → ArgoCD detects drift → auto-syncs to EKS
- Rollback = `git revert` → ArgoCD re-syncs

### CI/CD — GitHub Actions
```
.github/workflows/
├── build-python.yml   build + test + push Python service images
├── build-java.yml     build + test + push Java service images
└── infra.yml          terraform plan on PR, terraform apply on merge
```

---

## Build Order (recommended)

1. **auth** ✅ — add `/validate` + `/register`
2. **gateway** (Python/FastAPI) — unblocks all others
3. **user** (Java) — profiles, contacts
4. **chat** (Java) — message store
5. **websocket** (Python) — real-time layer
6. **presence** (Python) — Redis TTL
7. **media** (Java) — S3 uploads
8. **notification** (Python worker) — FCM push
9. **Terraform** — AWS infra
10. **Helm charts** — per service
11. **ArgoCD** — GitOps wiring
12. **GitHub Actions** — CI/CD pipelines

---

## Cross-Service TODOs

- [ ] API Gateway service
- [ ] Shared docker-compose for full local stack
- [ ] Centralized structured logging (ELK or CloudWatch)
- [ ] Terraform modules for AWS infra
- [ ] Helm chart per service
- [ ] ArgoCD app definitions
- [ ] GitHub Actions CI/CD pipelines
- [ ] External Secrets Operator for K8s ↔ AWS Secrets Manager
