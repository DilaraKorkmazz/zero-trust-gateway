import redis
from fastapi import HTTPException, status
from app.config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def check_rate_limit(client_ip: str, max_requests: int = 5, window_seconds: int = 60):
    key = f"rate_limit:{client_ip}"
    current_count = r.incr(key)
    
    if current_count == 1:
        r.expire(key, window_seconds)
        
    if current_count > max_requests:
        ttl = r.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )
