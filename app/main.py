import time
import json
import logging
from fastapi import FastAPI, Request, Depends
import httpx
from app.rate_limiter import check_rate_limit
from app.security import require_role

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler("audit.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
audit_logger.addHandler(handler)

app = FastAPI(title="Zero-Trust API Gateway")

@app.middleware("http")
async def audit_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    start_time = time.time()
    
    # Öffentliche Routen vom Rate Limiter ausnehmen
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
