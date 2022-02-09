import hashlib
import logging

from flask import request

logger = logging.getLogger(__name__)

def _post_request_cache_key():
    """Create cache keys based on request body."""
    # hash the request body so it can be
    # used as a key for cache.
    # only works within requests (app route functions)
    data = request.get_data(as_text=False)
    hash = str(hashlib.md5(data).hexdigest())
    key = request.path + hash
    logger.info(f"Cached {key} for {str(data)}")
    return key
