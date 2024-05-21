from botasaurus_requests.request_class import Request

def create_request(proxy=None,  user_agent=None):
    reqs = Request(
            proxy,
            user_agent
        )
    
    if proxy is not None:
        reqs.proxy =  proxy
      
        reqs.proxy = None
        
    return reqs
