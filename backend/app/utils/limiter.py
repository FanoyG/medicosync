from slowapi import Limiter
from slowapi.util import get_remote_address

# This is the single source of truth for your Guard
limiter = Limiter(key_func=get_remote_address)
