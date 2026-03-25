import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:5000")

ROUTES = {
    "user":     os.environ.get("USER_SERVICE_URL",     "http://user:8080"),
    "chat":     os.environ.get("CHAT_SERVICE_URL",     "http://chat:8080"),
    "media":    os.environ.get("MEDIA_SERVICE_URL",    "http://media:8080"),
    "ws":       os.environ.get("WS_SERVICE_URL",       "http://websocket:8000"),
    "presence": os.environ.get("PRESENCE_SERVICE_URL", "http://presence:5001"),
}

PUBLIC_PATHS = {"/health", "/auth/login", "/auth/register"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response("missing token", status_code=401)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{AUTH_SERVICE_URL}/validate",
                headers={"Authorization": auth_header},
            )
        except httpx.RequestError:
            return Response("auth service unavailable", status_code=503)

    if resp.status_code != 200:
        return Response(resp.text, status_code=resp.status_code)

    request.state.user_email = resp.json().get("email")

    return await call_next(request)


@app.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_auth(path: str, request: Request):
    return await _proxy(f"{AUTH_SERVICE_URL}/{path}", request, inject_user=False)


@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy(service: str, path: str, request: Request):
    target_base = ROUTES.get(service)
    if not target_base:
        return Response("service not found", status_code=404)
    return await _proxy(f"{target_base}/{path}", request, inject_user=True)


async def _proxy(url: str, request: Request, inject_user: bool) -> Response:
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if inject_user and hasattr(request.state, "user_email"):
        headers["X-User-Email"] = request.state.user_email

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
            )
        except httpx.RequestError as e:
            return Response(f"upstream error: {e}", status_code=503)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
