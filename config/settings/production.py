from .base import *
import os

if not DEBUG:
    allowed_hosts_string = os.getenv("ALLOWED_HOSTS")
    ALLOWED_HOSTS = allowed_hosts_string.split(',') if allowed_hosts_string else []
    