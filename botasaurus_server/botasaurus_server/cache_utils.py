import json
from hashlib import sha256
from datetime import datetime, timedelta, timezone
from .db_setup import Session
from .models import Cache
from .retry_on_db_error import retry_on_db_error

def is_expired(cache_entry, days):
    return datetime.now(timezone.utc).replace(tzinfo=None) > cache_entry.created_at + timedelta(days=days)

@retry_on_db_error
def get_cached_data(cache_key, days=180):
    with Session() as session:
        cache_entry = session.query(Cache).filter(Cache.key == cache_key).first()
        if cache_entry:
            if not is_expired(cache_entry, days):
                return True, cache_entry.data 
            else:
                session.delete(cache_entry)
                session.commit()
    return False, None

def create_cache_key(prefix, validated_data):
    serialized_data = json.dumps(validated_data).encode('utf-8')
    data_hash = sha256(serialized_data).hexdigest()    
    return prefix + '-' + data_hash

@retry_on_db_error
def set_cache_data(key, data):
    with Session() as session:
        cache_entry = session.query(Cache).filter(Cache.key == key).first()
        if cache_entry:
            cache_entry.data = data
        else:
            cache_entry = Cache(key=key, data=data)
            session.add(cache_entry)
        session.commit()
