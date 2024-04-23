from .anti_detect_requests import Request

def create_request(proxy=None,  user_agent=None, use_stealth=False,):
    # Use windows, chrome (most common) as mixing other platforms and browsers causes bot detection
    
    if use_stealth:
      if user_agent:
        raise ValueError("user_agent can not be used in stealth")
    
    if user_agent:
        reqs = Request(
            use_stealth=use_stealth,
            browser={
                'custom': user_agent,
            }
        )
    else:
        reqs = Request(
            use_stealth=use_stealth,
            browser={
                'platform': 'windows',
                'browser': 'chrome',
                'mobile': False
            }
        )
    if proxy is not None:
        reqs.proxy =  proxy
        reqs.proxies = {
            'http': proxy,
            'https': proxy,
        }
    else:
        reqs.proxy = None
        
    return reqs
