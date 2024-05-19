from botasaurus_requests import Request

def create_request(proxy=None,  ):
    reqs = Request(
            proxy=proxy,
        )
    
    if proxy is not None:
        reqs.proxy =  proxy
      
        reqs.proxy = None
        
    return reqs
