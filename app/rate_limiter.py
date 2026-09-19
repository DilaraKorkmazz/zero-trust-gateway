import time
import logging
from fastapi import HTTPException, status
from app.config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger("gateway")
memory_store = {}

def check_rate_limit(client_ip: str, max_requests: int = 5, window_seconds: int = 60):
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=0.2)
        current_count = r.incr(f"rate_limit:{client_ip}")
        if current_count == 1:
            r.expire(f"rate_limit:{client_ip}", window_seconds)
        if current_count > max_requests:
            ttl = r.ttl(f"rate_limit:{client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds."
            )
    except HTTPException:
        raise
    except Exception:
        now = time.time()
        requests = memory_store.get(client_ip, [])
        requests = [t for t in requests if now - t < window_seconds]
        if len(requests) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again shortly."
            )
        requests.append(now)
        memory_store[client_ip] = requests
