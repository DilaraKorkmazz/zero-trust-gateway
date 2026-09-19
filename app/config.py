import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey_do_not_use_in_prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
