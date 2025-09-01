import requests

from requests.adapters import HTTPAdapter
from urllib3 import Retry


def make_session() -> requests.Session:
    session = requests.Session()
    
    retries = Retry(
        total=5,
        connect=5,      
        read=5,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["HEAD","GET"])
    )
    
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    return session