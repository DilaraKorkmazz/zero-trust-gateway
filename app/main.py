import time
import json
import logging
import httpx
from fastapi import FastAPI, Request, Depends
from app.security import require_role
from app.rate_limiter import check_rate_limit

app = FastAPI(title="Zero-Trust API Gateway")

logging.basicConfig(level=logging.INFO)
audit_logger = logging.getLogger("audit")

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    start_time = time.time()

    if not request.url.path.startswith("/public"):
        try:
            check_rate_limit(client_ip)
        except Exception as exc:
            audit_logger.warning(json.dumps({
                "ip": client_ip, "path": request.url.path, "status": 429, "event": "RATE_LIMIT_BLOCKED"
            }))
            raise exc

    response = await call_next(request)
    duration = round(time.time() - start_time, 4)

    log_entry = {
        "ip": client_ip,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_sec": duration
    }
    audit_logger.info(json.dumps(log_entry))
    return response

@app.get("/public/health")
def health_check():
    return {"status": "gateway running", "zero_trust": "active"}

@app.get("/api/v1/internal/admin-data")
async def forward_admin_data(user: dict = Depends(require_role("admin"))):
    async with httpx.AsyncClient() as client:
        res = await client.get("http://internal-service:8001/admin-stats")
        return res.json()
