from .db_setup import Session
from .models import Cache
from .retry_on_db_error import retry_on_db_error

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
