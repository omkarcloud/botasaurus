id = None

def _get_id():
    global id
    if id is not None:
        return id

    from hashlib import md5
    from uuid import getnode

    id = md5(str(getnode()).encode('utf-8')).hexdigest()

    return id